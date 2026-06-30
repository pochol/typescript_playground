# 🔌 Most (relay) — komputer

Działa na komputerze z internetem. Co kilka minut ściąga nowe zdjęcia z
telefonu przez **ADB (USB)**, analizuje je **Claude'em**, i wysyła do **Firebase**.
To obejście braku internetu w telefonie — komputer jest mostem do chmury.

## Wymagania

- Python 3.10+
- `adb` (Android Platform Tools) w PATH
- Telefon z zainstalowaną aplikacją (`android/`), podłączony kablem,
  z włączonym debugowaniem USB
- Klucz API Anthropic (analiza AI) — opcjonalnie
- Projekt Firebase z włączonym Storage i Firestore — opcjonalnie

## Instalacja

```bash
cd relay
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # uzupełnij klucze
```

## Konfiguracja Firebase (jeśli chcesz dashboard w chmurze)

1. https://console.firebase.google.com → utwórz projekt
2. Build → **Firestore Database** → utwórz (tryb produkcyjny)
3. Build → **Storage** → włącz
4. Project settings → **Service accounts** → *Generate new private key* →
   zapisz JSON jako `relay/firebase-service-account.json`
5. W `.env` ustaw `FIREBASE_STORAGE_BUCKET` (np. `twoj-projekt.appspot.com`)

> Bez Firebase też zadziała — pliki i analiza wylądują lokalnie w
> `./photos/*.json` (tryb lokalny włącza się sam, gdy brak konfiguracji Firebase).

## Uruchomienie

```bash
source .venv/bin/activate
python relay.py
```

Zobaczysz log w stylu:

```
[14:23:01] Telefon podłączony: 1a2b3c4d
[14:23:01] AI: claude-opus-4-8
[14:23:02] Firebase: połączono.
[14:23:02] Start. Przetworzonych wcześniej: 0. Co 120s sprawdzam telefon.
[14:25:04] Nowe zdjęcia: 1
[14:25:09] ⬇️  growkit_20260630-142500.jpg (3120 KB)
[14:25:14] 🔬 growkit_20260630-142500.jpg: colonization (62% kol., piny=False)
[14:25:16] ☁️  Wysłano: https://storage.googleapis.com/...
```

## Test pojedynczego zdjęcia (sama analiza)

```bash
python analyzer.py ./photos/growkit_20260630-142500.jpg
```

## Jak to znosi awarie

- Przetworzone pliki zapisane w `state.json` — restart nie dubluje pracy.
- Błąd analizy/uploadu jednego zdjęcia nie zatrzymuje pętli.
- Odłączysz telefon → most czeka, po podłączeniu wznawia.
