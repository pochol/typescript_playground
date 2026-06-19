# 🚀 IPO Tracker — zbliżające się debiuty na giełdzie USA

Narzędzie, które pokazuje firmy wchodzące na giełdę amerykańską (NYSE / NASDAQ) —
tak jak zrobił to **SpaceX**. Cel: obserwować spółki **zanim** trafią na rynek,
żeby ocenić, czy warto je kupić (np. na **Revolut**, gdy pojawią się w ofercie).

## Co tu jest

| Plik | Opis |
|------|------|
| `index.html` | Gotowa, ładna strona z migawką zbliżających się IPO (otwórz w przeglądarce — działa bez niczego). |
| `ipo_tracker.py` | Skrypt w Pythonie, który **na żywo** odpytuje kalendarz IPO i generuje listę / raport HTML. |

## Szybki start

Otwórz po prostu `index.html` w przeglądarce — zobaczysz aktualną migawkę.

## Świeże dane przez Pythona

```bash
# 1. Darmowy klucz API (rejestracja: https://finnhub.io/register)
export FINNHUB_API_KEY="twoj_klucz"

# 2. IPO na najbliższy miesiąc (domyślnie dziś -> +30 dni)
python ipo_tracker.py

# Własny zakres dat
python ipo_tracker.py --from 2026-06-19 --to 2026-07-19

# Tylko NASDAQ
python ipo_tracker.py --exchange NASDAQ

# Wygeneruj raport HTML (nadpisze index.html świeżymi danymi)
python ipo_tracker.py --html index.html

# Surowe dane do JSON
python ipo_tracker.py --json ipos.json
```

Skrypt korzysta wyłącznie z biblioteki standardowej Pythona (3.9+) — nie trzeba
instalować żadnych zależności.

## Źródło danych

[Finnhub IPO Calendar](https://finnhub.io/docs/api/ipo-calendar) — darmowy plan
w zupełności wystarcza do śledzenia kalendarza IPO.

## ⚠️ Zastrzeżenie

To **nie jest porada inwestycyjna**. Daty i ceny IPO często się zmieniają lub bywają
odwoływane. Inwestowanie w akcje (zwłaszcza świeżych debiutów) wiąże się z ryzykiem
straty kapitału. Zawsze potwierdzaj dane w oficjalnym kalendarzu giełdy.
