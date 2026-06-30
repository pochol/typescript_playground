# 📱 Aplikacja Android — Mushroom Monitor

Aplikacja na **Xiaomi Mi 11** (Android 11+, API 30). Robi zdjęcia growkitu,
steruje lampą i **wysyła zdjęcia do komputera przez Bluetooth** (RFCOMM/SPP).
**Bez USB, bez internetu w telefonie.**

## Funkcje

- 📸 zdjęcie w **108 MP** (główny sensor) lub **12 MP** (pixel-binning, szybsza wysłka)
- 💡 lampa: **błysk** / **latarka** (ciągłe światło) / **bez**
- 📡 wysłka pliku **przez Bluetooth** do sparowanego komputera
- ⏱️ cykliczne zdjęcia co N minut (WorkManager, przeżywa restart)
- 🔆 budzi ekran na czas zdjęcia, na pierwszym planie trzyma ekran włączony

## Budowanie APK (na komputerze)

W **Android Studio** (Hedgehog+):

1. `File → Open` → wskaż katalog `android/`
2. Studio dociągnie zależności i wygeneruje wrapper Gradle
3. `Build → Build Bundle(s)/APK(s) → Build APK(s)`
4. APK: `app/build/outputs/apk/debug/app-debug.apk`

## Wgranie APK na telefon — BEZ USB

Telefon nie ma internetu, a USB odpada — więc sam plik APK też przenosimy
**przez Bluetooth**:

1. Sparuj telefon z komputerem w ustawieniach Bluetooth.
2. Z komputera **wyślij `app-debug.apk` na telefon przez Bluetooth**
   (wysyłanie pliku / „Send to device").
3. Na telefonie otwórz odebrany plik APK (z powiadomienia lub z Menedżera plików).
4. Zezwól „Instaluj z nieznanych źródeł" dla aplikacji, z której otwierasz APK
   (Menedżer plików / Bluetooth), i zainstaluj.

> Alternatywa bez USB i bez BT: skopiuj APK na kartę SD / pendrive przez OTG.

## Użycie

1. Ustaw telefon na statywie **na wprost** pojemnika z grzybnią — tak, by w kadrze
   był box z growkitami **oraz** wyświetlacz z wilgotnością i temperaturą.
2. Na komputerze uruchom odbiornik: [`../relay/README.md`](../relay/README.md).
3. W aplikacji daj zgody (aparat + Bluetooth), wciśnij **Odśwież listę** i wybierz
   swój komputer z listy sparowanych urządzeń.
4. Wybierz lampę (polecam **Latarka** — równe, powtarzalne światło między klatkami).
5. **„Zrób zdjęcie i wyślij"** — sprawdź, czy na komputerze pojawiło się zdjęcie.
6. Ustaw interwał (np. 30 min) i **„Start harmonogramu"**. Trzymaj telefon na
   ładowarce; po każdym zdjęciu plik leci po Bluetooth.

## ⚠️ 108 MP a Bluetooth

Mi 11 ma sensor **108 MP** (nie 120 MP — taki tryb nie istnieje). Plik 108 MP to
~30 MB — **przez Bluetooth idzie wolno** (nawet kilka minut). Do timelapse
rekomenduję **12 MP** (~3 MB): szybka wysłka i w zupełności wystarcza do analizy.
Pełne 108 MP włącz tylko, gdy chcesz móc przybliżać detale strzępek/pinów.

Jeśli MIUI zablokuje pełną rozdzielczość przez Camera2, aplikacja weźmie
automatycznie największą dostępną.

## Cykl gęstszy niż 15 min

WorkManager wymusza minimum 15 min dla pracy okresowej — dla grzybni aż nadto.
Gdybyś chciał gęściej, trzeba przejść na foreground service; powiedz, dopiszę.
