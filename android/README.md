# 📱 Aplikacja Android — Mushroom Monitor

Aplikacja na **Xiaomi Mi 11** (Android 11+, API 30). Robi zdjęcia growkitu
w pełnej rozdzielczości (108 MP), steruje lampą, i zapisuje pliki do folderu,
który komputer ściąga przez `adb pull`.

## Funkcje

- 📸 zdjęcie w **108 MP** (główny sensor) lub **12 MP** (pixel-binning, mniejszy plik)
- 💡 lampa: **błysk** / **latarka** (ciągłe światło) / **bez**
- ⏱️ cykliczne zdjęcia co N minut (WorkManager, przeżywa restart)
- 🔆 budzi ekran na czas zdjęcia, na pierwszym planie trzyma ekran włączony
- 💾 zapis do `Android/data/com.mushroom.monitor/files/Pictures/growkit/`

## Budowanie APK

Najprościej w **Android Studio** (Hedgehog+):

1. `File → Open` → wskaż katalog `android/`
2. Studio dociągnie zależności i wygeneruje wrapper Gradle automatycznie
3. `Build → Build Bundle(s)/APK(s) → Build APK(s)`
4. APK ląduje w `app/build/outputs/apk/debug/app-debug.apk`

Z linii poleceń (jeśli masz lokalny Gradle 8.7+):

```bash
cd android
gradle wrapper          # jednorazowo, generuje ./gradlew
./gradlew assembleDebug
```

## Instalacja na telefonie (przez USB)

1. W telefonie: `Ustawienia → Informacje → MIUI` — 7× tapnij „Wersja MIUI"
   (włącza opcje deweloperskie)
2. `Ustawienia → Dodatkowe → Opcje programisty` → włącz **Debugowanie USB**
   oraz **Instaluj przez USB**
3. Podłącz telefon kablem, zatwierdź „Zezwól na debugowanie USB"
4. Zainstaluj:

```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

## Użycie

1. Ustaw telefon na statywie **na wprost** pojemnika z grzybnią — tak, żeby w
   kadrze był box z growkitami **oraz** wyświetlacz z wilgotnością i temperaturą.
2. Otwórz aplikację, daj zgodę na aparat.
3. Wybierz lampę (na start polecam **Latarka** — równe, powtarzalne światło
   między zdjęciami, kluczowe dla porównywania klatek w czasie).
4. **„Zrób zdjęcie teraz"** — sprawdź kadr i ostrość na podglądzie pliku.
5. Ustaw interwał (np. 30 min) i **„Start harmonogramu"**.
6. Zostaw telefon podłączony do ładowarki/komputera. Most (`relay/`) zajmie się resztą.

## ⚠️ Uwaga o 108 MP

Mi 11 ma sensor **108 MP** (12000×9000) — **nie ma trybu 120 MP**, on nie
istnieje na tym sprzęcie. Aplikacja bierze największy rozmiar JPEG, jaki sensor
zgłasza przez Camera2. Na większości egzemplarzy Mi 11 to pełne 108 MP. Jeśli na
Twoim Xiaomi zablokowało pełną rozdzielczość przez Camera2 (zdarza się w niektórych
buildach MIUI), aplikacja automatycznie weźmie największą dostępną — a Ty możesz
odznaczyć „Pełna rozdzielczość", żeby świadomie strzelać 12 MP.

**Rekomendacja do analizy:** 12 MP zwykle wystarcza, daje 10× mniejsze pliki
(~3 MB vs ~30 MB), szybszy `adb pull` i tańszą analizę AI. 108 MP zostaw, jeśli
chcesz móc przybliżać detale strzępek/pinów.

## Gęstszy timelapse niż 15 min

WorkManager ma twardy limit min. 15 min dla pracy okresowej. Dla grzybni to
aż nadto (zmiany są powolne). Gdybyś chciał gęściej — trzeba przejść na
foreground service z własną pętlą; powiedz, dopiszę.
