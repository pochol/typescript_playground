#!/usr/bin/env python3
"""Most: telefon (ADB) → analiza Claude → Firebase.

Pętla:
  1. `adb shell ls` listuje zdjęcia w folderze aplikacji na telefonie
  2. nowe pliki ściąga przez `adb pull`
  3. analizuje je modelem Claude (chyba że DISABLE_AI=1)
  4. wysyła zdjęcie + analizę do Firebase (Storage + Firestore)
  5. zapamiętuje przetworzone pliki w state.json i czeka POLL_INTERVAL_SECONDS

Uruchom z podłączonym telefonem (włączone debugowanie USB):
    python relay.py
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PHONE_DIR = os.environ.get(
    "PHONE_PHOTOS_DIR",
    "/sdcard/Android/data/com.mushroom.monitor/files/Pictures/growkit",
)
LOCAL_DIR = Path(os.environ.get("LOCAL_PHOTOS_DIR", "./photos"))
POLL = int(os.environ.get("POLL_INTERVAL_SECONDS", "120"))
DISABLE_AI = os.environ.get("DISABLE_AI", "0") == "1"
STATE_FILE = Path("./state.json")

FNAME_RE = re.compile(r"growkit_(\d{8})-(\d{6})\.jpg$")


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def adb(*args: str) -> str:
    """Uruchom polecenie adb i zwróć stdout (tekst)."""
    result = subprocess.run(
        ["adb", *args], capture_output=True, text=True, timeout=300
    )
    if result.returncode != 0:
        raise RuntimeError(f"adb {' '.join(args)} -> {result.stderr.strip()}")
    return result.stdout


def check_device() -> None:
    out = adb("devices")
    lines = [l for l in out.splitlines()[1:] if l.strip() and "device" in l]
    if not lines:
        log("⚠️  Nie wykryto telefonu. Podłącz kabel i włącz debugowanie USB.")
        sys.exit(1)
    log(f"Telefon podłączony: {lines[0].split()[0]}")


def list_remote_photos() -> list[str]:
    try:
        out = adb("shell", "ls", "-1", PHONE_DIR)
    except RuntimeError:
        log(f"⚠️  Folder {PHONE_DIR} pusty lub niedostępny (jeszcze brak zdjęć?).")
        return []
    return sorted(n.strip() for n in out.splitlines()
                  if n.strip().endswith(".jpg"))


def captured_at_ms(filename: str) -> int:
    """Wyciąga znacznik czasu z nazwy growkit_YYYYMMDD-HHMMSS.jpg."""
    m = FNAME_RE.search(filename)
    if not m:
        return int(time.time() * 1000)
    dt = datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
    return int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)


def load_state() -> set[str]:
    if STATE_FILE.exists():
        return set(json.loads(STATE_FILE.read_text()).get("processed", []))
    return set()


def save_state(processed: set[str]) -> None:
    STATE_FILE.write_text(json.dumps({"processed": sorted(processed)}, indent=2))


def main() -> None:
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    check_device()

    analyzer = None
    uploader = None
    if not DISABLE_AI:
        from analyzer import Analyzer
        analyzer = Analyzer()
        log(f"AI: {analyzer.model}")
    else:
        log("AI wyłączone (DISABLE_AI=1) — tylko ściąganie + upload.")

    # Upload jest opcjonalny — jeśli brak konfiguracji Firebase, działamy lokalnie.
    try:
        from uploader import Uploader
        uploader = Uploader()
        log("Firebase: połączono.")
    except Exception as e:  # noqa: BLE001
        log(f"⚠️  Firebase niedostępne ({e}). Pliki zostaną tylko lokalnie + JSON.")

    processed = load_state()
    log(f"Start. Przetworzonych wcześniej: {len(processed)}. Co {POLL}s sprawdzam telefon.")

    while True:
        try:
            remote = list_remote_photos()
            new = [f for f in remote if f not in processed]
            if new:
                log(f"Nowe zdjęcia: {len(new)}")
            for fname in new:
                local_path = LOCAL_DIR / fname
                adb("pull", f"{PHONE_DIR}/{fname}", str(local_path))
                log(f"⬇️  {fname} ({local_path.stat().st_size // 1024} KB)")

                analysis = None
                if analyzer:
                    try:
                        analysis = analyzer.analyze(str(local_path)).to_dict()
                        log(f"🔬 {fname}: {analysis['stage']} "
                            f"({analysis['colonization_pct']}% kol., "
                            f"piny={analysis['pins_detected']})")
                    except Exception as e:  # noqa: BLE001
                        log(f"⚠️  Analiza {fname} nie powiodła się: {e}")

                doc_id = fname.removesuffix(".jpg")
                ts = captured_at_ms(fname)
                if uploader:
                    try:
                        url = uploader.upload(str(local_path), doc_id, ts, analysis)
                        log(f"☁️  Wysłano: {url}")
                    except Exception as e:  # noqa: BLE001
                        log(f"⚠️  Upload {fname} nie powiódł się: {e}")
                else:
                    # tryb lokalny: zapisz analizę obok zdjęcia
                    (LOCAL_DIR / f"{doc_id}.json").write_text(
                        json.dumps(
                            {"id": doc_id, "capturedAt": ts, "analysis": analysis},
                            indent=2, ensure_ascii=False,
                        )
                    )

                processed.add(fname)
                save_state(processed)
        except KeyboardInterrupt:
            log("Zatrzymano.")
            break
        except Exception as e:  # noqa: BLE001
            log(f"⚠️  Błąd pętli: {e}")
        time.sleep(POLL)


if __name__ == "__main__":
    main()
