# 📊 Dashboard (opcjonalny) — wariant React

> **Nie jest potrzebny do działania projektu.** Domyślny, lokalny dashboard to
> `photos/report.html` generowany przez `relay/report.py` — otwierasz go
> dwuklikiem, bez instalacji i bez internetu.
>
> Ten folder to ładniejsza, opcjonalna alternatywa (React + TypeScript) dla osob,
> które wolą pełny interfejs. Czyta te same dane (`Photo` + `Analysis` z
> [`src/types.ts`](src/types.ts)).

## Uruchomienie (tryb DEMO)

```bash
cd dashboard
npm install
npm run dev          # http://localhost:5173 — pokazuje dane przykładowe
```

Bez konfiguracji startuje w **trybie DEMO** (dane przykładowe), żeby pokazać
jak wygląda układ.

## Podpięcie pod dane lokalne

Ten wariant powstał jeszcze przy architekturze chmurowej (Firebase). Przy
obecnym, **w pełni lokalnym** podejściu rekomendowany jest `photos/report.html`.
Jeśli chcesz, żeby ten React czytał lokalny folder ze zdjęciami — powiedz,
dorobię prosty loader `photos/index.json` zamiast Firebase.
