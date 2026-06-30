# 🔌 Odbiornik Bluetooth (relay) — komputer

Działa na komputerze **sparowanym z telefonem przez Bluetooth**. Odbiera zdjęcia
wysyłane przez aplikację, (opcjonalnie) analizuje je **Claude'em**, zapisuje
lokalnie i generuje raport `photos/report.html`. **Bez chmury, bez USB.**

## Wymagania

- Python 3.10+
- **PyBluez** (klasyczny Bluetooth / RFCOMM)
  - Linux: `sudo apt install libbluetooth-dev` a potem `pip install PyBluez`
  - Windows: zwykle działa z natywnym stosem Bluetooth
  - macOS: PyBluez bywa kłopotliwy — patrz sekcja *macOS* niżej
- (opcjonalnie) klucz API Anthropic — tylko gdy chcesz analizę AI

## Instalacja

```bash
cd relay
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # uzupełnij (albo zostaw DISABLE_AI=1 dla trybu offline)
```

## Parowanie (raz)

W ustawieniach systemu **sparuj telefon z komputerem** przez Bluetooth.
Dopiero sparowane urządzenie pokaże się na liście w aplikacji.

## Uruchomienie

```bash
source .venv/bin/activate
python bt_receiver.py
```

Zobaczysz np.:

```
[14:23:01] AI: claude-opus-4-8
[14:23:01] Nasłuch Bluetooth (RFCOMM), kanał 3. Czekam na telefon… (Ctrl+C kończy)
[14:25:09] Połączono: ('A1:B2:C3:D4:E5:F6', 3)
[14:25:12] ⬇️  growkit_20260630-142500.jpg (3120 KB)
[14:25:17] 🔬 growkit_20260630-142500.jpg: colonization (62% kol., piny=False)
[14:25:17] 📊 Raport odświeżony: photos/report.html
```

Otwórz **`photos/report.html`** dwuklikiem — to Twój dashboard. Odświeża się
przy każdym nowym zdjęciu (wystarczy F5 w przeglądarce).

## Tryb w pełni offline

Ustaw w `.env`:
```
DISABLE_AI=1
```
Wtedy nic nie wychodzi do internetu — odbierasz zdjęcia i oglądasz galerię
(bez ocen AI). Ręczny raport: `python report.py`.

## macOS

PyBluez na nowym macOS bywa nie do skompilowania. Jeśli tak — napisz, podmienię
odbiornik na wariant przez **system Bluetooth (OBEX/AirDrop folder)** albo
na mały most w innym języku. Na Linux/Windows PyBluez działa najlepiej.

## Test generatora raportu (bez Bluetooth)

```bash
python report.py        # zbuduje photos/report.html z tego, co już jest w ./photos
```
