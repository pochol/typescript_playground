# 🍄 Mushroom Growth Monitor

System do monitorowania wzrostu grzybni (growkity) z telefonu **Xiaomi Mi 11**
bez dostępu do internetu/WiFi, z dashboardem do obserwacji i analizą zdjęć AI.

## Problem

Telefon ma zepsutą płytę główną — WiFi nie działa, internetu brak, SIM nie
przekładamy. Trzeba więc robić zdjęcia growkitu (grzybnia + widoczny odczyt
wilgotności i temperatury w boxie) i przesyłać je do komputera **bez sieci**.

## Architektura

```
Telefon Mi 11 (bez internetu)        Komputer (z internetem)            Ty
┌──────────────────────────┐  USB/ADB  ┌────────────────────┐  Firebase  ┌────────────┐
│ android/  (APK, Kotlin)  │ ───────►  │ relay/ (Python)    │ ────────►  │ dashboard/ │
│ • budzi ekran            │   pull    │ • adb pull         │   upload   │ (React+TS) │
│ • aparat 108 MP          │           │ • analiza Claude   │            │ • galeria  │
│ • steruje lampą          │           │ • OCR temp/wilg.   │            │ • timeline │
│ • spust + zapis          │           │ • upload Firebase  │            │ • wykresy  │
│ • powtórka co N minut    │           └────────────────────┘            │ • alerty   │
└──────────────────────────┘                                             └────────────┘
```

**Dlaczego tak?** Telefon nie ma internetu, więc nie wrzuci nic do chmury sam.
Komputer (który ma sieć) działa jako **most**: przez kabel USB + ADB ściąga
nowe zdjęcia, analizuje je modelem wizyjnym Claude, i publikuje na Firebase.
Dashboard React czyta z Firebase — oglądasz wzrost z dowolnego urządzenia.

## Komponenty

| Katalog      | Co to                                   | Stack                             |
|--------------|-----------------------------------------|-----------------------------------|
| `android/`   | Aplikacja APK na Mi 11                  | Kotlin, Camera2, WorkManager      |
| `relay/`     | Most na komputerze (pull → AI → upload) | Python 3, adb, Anthropic SDK      |
| `dashboard/` | Panel obserwacji + analiza              | React, TypeScript, Vite, Firebase |

## Szybki start

1. **APK** — zbuduj i wgraj na telefon: [`android/README.md`](android/README.md)
2. **Most** — uruchom na komputerze z podłączonym telefonem: [`relay/README.md`](relay/README.md)
3. **Dashboard** — uruchom panel: [`dashboard/README.md`](dashboard/README.md)

## Co obserwujemy (eksperyment)

Cel: nauczyć się po ~30 zdjęciach, **kiedy grzybnia zaczyna wychodzić na
zewnątrz** (pinning → owocniki). Zmienne mierzone ze zdjęcia:

- **% pokrycia grzybnią** (ile białego) — postęp kolonizacji
- **wykrycie pierwszych zawiązków/pinów** — start owocowania
- **morfologia** — długie „nóżki" (trzony) vs. duże kapelusze (sygnał warunków)
- **kondensacja / krople** na ściankach — nadmiar wilgoci
- **odczyt temperatury i wilgotności** z wyświetlacza w boxie (OCR + AI)

> ⚠️ **Uwaga sprzętowa:** Mi 11 ma aparat **108 MP** (nie 120 MP — taki tryb
> nie istnieje na tym sprzęcie). Aplikacja używa pełnej rozdzielczości sensora;
> w razie blokady Xiaomi można przełączyć na 12 MP (pixel-binning, mniejszy plik,
> często lepszy do analizy). Patrz `android/README.md`.
