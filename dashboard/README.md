# 📊 Dashboard — Mushroom Growth Monitor

Panel React + TypeScript (Vite) do obserwacji wzrostu grzybni. Czyta zdjęcia
i analizy z Firebase (publikowane przez `relay/`) i pokazuje na żywo:

- 📈 wykres **postępu kolonizacji** (%) w czasie
- 🌡️💧 wykres **temperatury i wilgotności** odczytanych z wyświetlacza w boxie
- 🌱 **alert pinningu** — kiedy pojawiły się pierwsze zawiązki (start owocowania)
- 🖼️ **galerię** wszystkich zdjęć z analizą AI (etap, morfologia, kondensacja,
  problemy, zalecenia)

## Uruchomienie

```bash
cd dashboard
npm install
npm run dev          # http://localhost:5173
```

Bez konfiguracji Firebase dashboard startuje w **trybie DEMO** (dane przykładowe),
żebyś od razu zobaczył jak wygląda.

## Podłączenie do Firebase

1. Firebase console → Project settings → General → Your apps → **Web app**
2. Skopiuj `firebaseConfig`
3. `cp .env.example .env.local` i uzupełnij wartości `VITE_FIREBASE_*`
4. `npm run dev` — dashboard przełączy się na dane na żywo

### Reguły dostępu (do odczytu publicznego)

W Firestore (`Rules`) na czas eksperymentu możesz dać odczyt publiczny:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{db}/documents {
    match /growkit_photos/{id} {
      allow read: if true;       // dashboard czyta
      allow write: if false;     // zapisuje tylko relay (service account, omija reguły)
    }
  }
}
```

## Build produkcyjny / hosting

```bash
npm run build        # -> dist/
```

`dist/` wrzuć na Firebase Hosting, Netlify, Vercel albo dowolny statyczny hosting.

## Skąd te dane

Każdy dokument w kolekcji `growkit_photos` ma kształt zdefiniowany w
[`src/types.ts`](src/types.ts) (`Photo` + `Analysis`) i jest tworzony przez
`relay/uploader.py`.
