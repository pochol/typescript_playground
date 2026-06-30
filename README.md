# 🍄 Mushroom Growth Monitor

Monitorowanie wzrostu grzybni (growkity) z telefonu **Xiaomi Mi 11**, **w pełni
lokalnie** — zdjęcia lecą z telefonu do komputera **przez Bluetooth**, bez
internetu i bez chmury. Na komputerze powstaje lokalny raport HTML z galerią
i analizą zdjęć.

> 🔒 Zasady projektu spisane w [`REQUIREMENTS.md`](REQUIREMENTS.md):
> **tylko Bluetooth**, **wszystko lokalnie**, dane nigdy nie idą do gita.

## Problem

Telefon ma zepsutą płytę główną — WiFi/internet nie działa, SIM nie przekładamy.
Transfer zdjęć do komputera idzie **wyłącznie przez Bluetooth**.

## Architektura

```
Telefon Mi 11 (bez internetu)      Bluetooth        Komputer (lokalnie)
┌──────────────────────────┐    (RFCOMM/SPP)   ┌────────────────────────┐
│ android/  (APK, Kotlin)  │ ════════════════► │ relay/bt_receiver.py   │
│ • aparat 108 MP          │                   │ • odbiera plik         │
│ • lampa (błysk/latarka)  │                   │ • analiza (opcj. Claude)│
│ • wysyła zdjęcie po BT   │                   │ • zapis do ./photos/   │
│ • cyklicznie co N minut  │                   │ • report.py → HTML     │
└──────────────────────────┘                   └────────────────────────┘
                                                          │
                                                          ▼
                                            photos/report.html (dwuklik)
```

## Komponenty

| Katalog      | Co to                                  | Stack                         |
|--------------|----------------------------------------|-------------------------------|
| `android/`   | Aplikacja APK na Mi 11                 | Kotlin, Camera2, Bluetooth RFCOMM, WorkManager |
| `relay/`     | Odbiornik BT + analiza + raport lokalny| Python 3, PyBluez, Anthropic SDK (opcj.) |
| `dashboard/` | (opcjonalny) wariant React            | React, TypeScript, Vite       |

> Do działania **wystarczą** `android/` + `relay/`. Folder `dashboard/` to
> opcjonalna, ładniejsza alternatywa dla `report.html` — niewymagana.

## Szybki start

1. **Sparuj** telefon z komputerem w ustawieniach Bluetooth (raz).
2. **APK** — zbuduj i wgraj na telefon: [`android/README.md`](android/README.md)
3. **Odbiornik** — uruchom na komputerze: [`relay/README.md`](relay/README.md)
4. W aplikacji wybierz komputer z listy sparowanych, ustaw lampę i interwał,
   wciśnij **Start**. Zdjęcia będą lecieć po Bluetooth, a na komputerze
   pojawi się `photos/report.html`.

## Co obserwujemy (eksperyment)

Cel: po ~30 zdjęciach rozpoznać, **kiedy grzybnia wychodzi na zewnątrz**
(pinning → owocniki). Zmienne ze zdjęcia: % kolonizacji, wykrycie pierwszych
zawiązków, morfologia (długie nóżki vs duże kapelusze), kondensacja, oraz odczyt
temperatury i wilgotności z wyświetlacza w boxie.

> ⚠️ Mi 11 ma aparat **108 MP** (nie 120 MP — taki tryb nie istnieje). Przez
> Bluetooth pliki 108 MP (~30 MB) idą **wolno**; do timelapse poleca się tryb
> **12 MP** (~3 MB) — szybszy transfer, w zupełności wystarcza do analizy.
