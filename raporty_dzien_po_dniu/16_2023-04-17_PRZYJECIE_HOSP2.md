# 17.04.2023 (Poniedziałek) - PONOWNE PRZYJĘCIE DO SZPITALA

## 📍 Status: SOR → Przyjęcie na Chirurgię (NOC)

---

## 📱 WhatsApp Mama
| Godzina | Nadawca | Treść | Znaczenie |
|---------|---------|-------|-----------|
| **22:07** | Mama | *"Wzięli Cię na jakieś badania?"* | Na SOR |
| **22:07** | Pacjent | *"Leżę na SOR pod kroplówką"* | |
| 22:09 | Mama | "To poczekamy jeszcze, jak będziesz miał okazję to podpytaj żebyśmy tu nie siedzieli do rana" | |
| **23:16** | Pacjent | *"Miałem tomografię"* | TK |
| **23:16** | Pacjent | *"Wysyłają mnie na chirurgię"* | Przyjęcie |
| **23:16** | Pacjent | *"Mam jakiś zbiornik płynu przy jelicie"* | **ROPIEŃ!** |
| **23:17** | Pacjent | *"I będą musieli mi go rozcinać prawdopodobnie"* | **DRENAŻ** |
| 23:19 | Mama | "To trzymaj się, będziemy w kontakcie" | |
| **23:40** | Pacjent | *"Ogólnie to na korytarzu leżę"* | **BRAK MIEJSCA** |
| 23:44 | Mama | "Na oddziale chirurgii jesteś" | |
| 23:53 | Pacjent | "Wszystko możecie przywieźć pls" | Rodzice jadą nocą |

### 📱 Messenger (Wybrane)

| Godzina | Nadawca | Treść | Znaczenie |
| :--- | :--- | :--- | :--- |
| **21:59** | Michał Wiencek | *"Chuj bede mial operacje"* | Potwierdzenie konieczności zabiegu. |
| **21:59** | Michał Wiencek | *"W Krakowie to mnie chyba z miesiąc nie bedzie"* | Pesymistyczna (i trafna) ocena długości leczenia. |
| **21:59** | Michał Wiencek | *"Zajebiscie"* | Sarkazm/rezygnacja. |
| **22:10** | Radek Salwach | *"tragedia Więcuś"* | Reakcja otoczenia. |
| 12:41 | Pacjent | *"Bo prawdopodobnie bede do szpitala jechal kurwa znowu..."* | Przewidywanie ponownej hospitalizacji przed zajęciami. |


---

## 🔴 KLUCZOWE FAKTY

1. **TK WYKAZAŁA ROPIEŃ** - *"zbiornik płynu przy jelicie"*
2. **KONIECZNOŚĆ DRENAŻU** - *"będą mi go rozcinać"*
3. **PACJENT LEŻY NA KORYTARZU** - brak miejsca na oddziale
4. **RODZICE JADĄ NOCĄ** - przywożą rzeczy
5. **10 DNI PO PIERWSZYM WYPISIE** - stan się pogorszył

---

## 🏥 DANE Z DOKUMENTACJI (BŁĘDY PRZYJĘCIA)

### 1. Błąd Organizacyjny (Zły Oddział)
Pacjent z chorobą Leśniowskiego-Crohna został przyjęty na **Oddział Chirurgii Naczyniowej i Ogólnej**, zamiast na Gastroenterologię (gdzie był wcześniej).
*   **Status:** Błąd 6.8 w `PELNA_LISTA_BLEDOW...`.
*   **Skutek:** Leczenie przez chirurgów naczyniowych, którzy nie mają doświadczenia w leczeniu biologicznym i zachowawczym IBD (późniejsze decyzje o operacji "z desperacji").

### 🩺 Diagnoza i Stan Zdrowia
*   **Wstępne rozpoznanie:** Ropień wewątrzbrzuszny (potwierdzony w badaniu fizykalnym i wywiadzie).
*   **Stan:** "Cierpiący", leży na korytarzu.
*   **Plan:** Drenaż (zaplanowany, ale opóźniony).

### 📄 DOKUMENTACJA MEDYCZNA (Weryfikacja)
*(Na podstawie `2023.04.17 godz.23.18 1.txt` - Skierowanie do Szpitala / Izba Przyjęć)*
*   **Wstępne rozpoznanie:** `R10.4 - Inny i nieokreślony ból brzucha`.
*   **Decyzje:**
    *   Skierowanie na Oddział Chirurgii Ogólnej wystawione o **23:18**.
    *   Potwierdzenie przyjęcia w trybie nagłym ("S1.3 - Przyj. w trybie nagłym - inne przypadki").
*   **Stan:** Dokument potwierdza "nagły" charakter przyjęcia, co kłóci się z wielogodzinnym oczekiwaniem i "leżeniem na korytarzu" opisywanym przez pacjenta. Czas wystawienia skierowania (23:18) sugeruje, że procedury trwały bardzo długo (pacjent był w szpitalu od popołudnia).

### 🚩 Uwagi Śledcze
> [!WARNING]
> **OPÓŹNIENIE PROCEDURALNE:**
> Pacjent zgłosił się do szpitala w godzinach popołudniowych (ok. 16:00-17:00, wg Messengera), a oficjalne skierowanie z Izby Przyjęć na Oddział wystawiono dopiero o **23:18**. To oznacza **6-7 godzin** oczekiwania na formalne przyjęcie, w trakcie których pacjent cierpiał bez adekwatnej pomocy (tylko Pyralgina).

### 🔗 Źródła
*   `temp_extraction.txt` (Messenger)
*   `2023.04.17 godz.23.18 1.pdf` (Skierowanie)

### 🚩 Uwagi Śledcze
> [!WARNING]
> **ZANIECHANIE LECZENIA BÓLU:**
> Dokumentacja potwierdza, że w dniu przyjęcia (17.04) przy rozpoznanym potężnym ropniu, pacjent otrzymał jedynie Pyralginę (lek niesteroidowy, za słaby na taki stan). Brak zleceń na opioidy w dokumentacji koreluje z dramatycznymi wiadomościami pacjenta.

### 🔗 Źródła
*   `temp_extraction.txt` (Messenger)
*   `Karta zleceń lekarskich 2023-04-17 do 2023-05-05.pdf` (Weryfikacja leków)

### 2. Błąd Diagnostyczny (TK bez kontrastu doustnego)
Wykonane o 23:16 TK opisano jako "ograniczonej wartości".
*   **Zaniechanie:** Brak podania kontrastu doustnego przed drenażem (Błąd 2.1).
*   **Ryzyko:** Drenaż "na ślepo" (lub na podstawie niepełnego obrazu), co zwiększa ryzyko uszkodzenia jelit lub niedostatecznego opróżnienia ropnia (co nastąpiło - ropień nawrócił 28.04).

---

## ⚠️ UWAGI ŚLEDCZE

> **[KRYTYCZNE]** Pacjent wypisany 07.04, wrócił 17.04 z ropniem wymagającym drenażu. **CZY PIERWSZY WYPIS BYŁ PRZEDWCZESNY?** Czy ropień nie powinien być zdiagnozowany i leczony podczas pierwszej hospitalizacji?

---

## 📂 ŹRÓDŁA
- `whsats up/mama/Czat WhatsApp z Mama.txt` (linie 1500-1526)
