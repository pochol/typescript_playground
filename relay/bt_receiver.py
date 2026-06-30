#!/usr/bin/env python3
"""Odbiornik Bluetooth (RFCOMM) — komputer.

Nasłuchuje po Bluetooth, odbiera zdjęcia wysyłane przez aplikację z telefonu,
zapisuje je lokalnie, (opcjonalnie) analizuje modelem Claude i odświeża lokalny
raport HTML. Działa w pełni lokalnie — bez chmury i bez internetu w ścieżce
danych (internet potrzebny tylko do opcjonalnej analizy AI).

Protokół (zgodny z BluetoothSender.kt w aplikacji):
    [int32 BE: długość nazwy][nazwa UTF-8][int64 BE: rozmiar][bajty pliku]

Uruchom na komputerze SPAROWANYM z telefonem:
    python bt_receiver.py
"""
from __future__ import annotations

import json
import os
import re
import struct
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

try:
    import bluetooth  # PyBluez
except ImportError:
    print("Brak PyBluez. Zainstaluj zależności: pip install -r requirements.txt")
    sys.exit(1)

LOCAL_DIR = Path(os.environ.get("LOCAL_PHOTOS_DIR", "./photos"))
DISABLE_AI = os.environ.get("DISABLE_AI", "0") == "1"
# Standardowy SPP UUID — ten sam wystawia telefon.
SPP_UUID = "00001101-0000-1000-8000-00805F9B34FB"
FNAME_RE = re.compile(r"growkit_(\d{8})-(\d{6})\.jpg$")


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def captured_at_ms(filename: str) -> int:
    m = FNAME_RE.search(filename)
    if not m:
        return int(time.time() * 1000)
    dt = datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
    return int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)


def recvall(sock, n: int) -> bytes:
    """Odbiera dokładnie n bajtów (recv może zwrócić mniej)."""
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(min(4096, n - len(buf)))
        if not chunk:
            raise ConnectionError("Połączenie przerwane")
        buf += chunk
    return buf


def receive_file(sock) -> tuple[str, bytes]:
    name_len = struct.unpack(">i", recvall(sock, 4))[0]
    name = recvall(sock, name_len).decode("utf-8")
    size = struct.unpack(">q", recvall(sock, 8))[0]
    data = recvall(sock, size)
    return name, data


def main() -> None:
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)

    analyzer = None
    if not DISABLE_AI:
        try:
            from analyzer import Analyzer
            analyzer = Analyzer()
            log(f"AI: {analyzer.model}")
        except Exception as e:  # noqa: BLE001
            log(f"AI niedostępne ({e}) — działam bez analizy.")
    else:
        log("AI wyłączone (DISABLE_AI=1) — tylko odbiór + galeria.")

    from report import build as build_report

    server = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server.bind(("", bluetooth.PORT_ANY))
    server.listen(1)
    port = server.getsockname()[1]
    try:
        bluetooth.advertise_service(
            server, "MushroomReceiver", service_id=SPP_UUID,
            service_classes=[SPP_UUID, bluetooth.SERIAL_PORT_CLASS],
            profiles=[bluetooth.SERIAL_PORT_PROFILE],
        )
    except Exception as e:  # noqa: BLE001
        log(f"⚠️  advertise_service nie powiodło się ({e}). "
            f"W aplikacji wybierz połączenie do tego komputera na kanale {port}.")

    log(f"Nasłuch Bluetooth (RFCOMM), kanał {port}. Czekam na telefon… (Ctrl+C kończy)")

    try:
        while True:
            client, addr = server.accept()
            log(f"Połączono: {addr}")
            try:
                while True:
                    name, data = receive_file(client)
                    path = LOCAL_DIR / name
                    path.write_bytes(data)
                    log(f"⬇️  {name} ({len(data) // 1024} KB)")

                    analysis = None
                    if analyzer:
                        try:
                            analysis = analyzer.analyze(str(path)).to_dict()
                            log(f"🔬 {name}: {analysis['stage']} "
                                f"({analysis['colonization_pct']}% kol., "
                                f"piny={analysis['pins_detected']})")
                        except Exception as e:  # noqa: BLE001
                            log(f"⚠️  Analiza {name} nie powiodła się: {e}")

                    sidecar = LOCAL_DIR / (path.stem + ".json")
                    sidecar.write_text(
                        json.dumps(
                            {"id": path.stem, "capturedAt": captured_at_ms(name),
                             "analysis": analysis},
                            indent=2, ensure_ascii=False,
                        ),
                        encoding="utf-8",
                    )
                    out = build_report(LOCAL_DIR)
                    log(f"📊 Raport odświeżony: {out}")
            except (ConnectionError, OSError) as e:
                log(f"Rozłączono ({e}). Czekam na ponowne połączenie…")
            finally:
                try:
                    client.close()
                except Exception:  # noqa: BLE001
                    pass
    except KeyboardInterrupt:
        log("Koniec.")
    finally:
        server.close()


if __name__ == "__main__":
    main()
