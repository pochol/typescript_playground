# Wymagania projektu (zapisane na życzenie użytkownika)

> DECYZJE ZABLOKOWANE — nie zmieniać bez wyraźnej zgody użytkownika.

1. **Transfer: WYŁĄCZNIE Bluetooth.** Żadnego USB, żadnego kabla, żadnego `adb`.
2. **Wszystko lokalnie.** Dane (zdjęcia) zostają na **telefonie + komputerze**.
   Zero chmury, zero Firebase, zero internetu w ścieżce danych.
   - *Jedyny wyjątek:* analiza AI (Claude) woła internet z komputera. Można ją
     wyłączyć ustawiając `DISABLE_AI=1` — wtedy całość działa offline.
3. **Dane/zdjęcia NIGDY nie trafiają do gita.** Repozytorium git zawiera wyłącznie
   **kod programu** (aplikacja + skrypty). Żadnych zdjęć ani danych z growkitu.
4. **Telefon:** Xiaomi Mi 11, aparat **108 MP** (tryb 120 MP nie istnieje na tym sprzęcie).
5. **Cel eksperymentu:** wykryć moment **pinningu** (wyjście grzybni na zewnątrz /
   start owocowania) oraz obserwować zmienne: % kolonizacji, morfologia
   (długie nóżki / duże kapelusze), kondensacja, temperatura i wilgotność
   (odczyt z wyświetlacza w boxie).

## Przepływ (architektura)

```
Xiaomi Mi 11  ──Bluetooth (RFCOMM)──►  Komputer
  aplikacja:                            bt_receiver.py:
  • aparat 108 MP                       • odbiera plik
  • lampa                               • analiza (opcjonalnie Claude)
  • wysyła zdjęcie po BT                • zapis lokalny
                                        • report.py → report.html (dwuklik)
```

Dashboard = lokalny plik `photos/report.html`, otwierany dwuklikiem w przeglądarce.
Komputer nie musi mieć internetu (poza opcjonalną analizą AI).
