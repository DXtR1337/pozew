# 🔴 AUDYT PRAWNY WNIOSKU RPP V3
## PERSPEKTYWA RED TEAM (PRAWNIK SZPITALA/PZU)

**Data audytu:** 15.01.2026  
**Dokument:** WNIOSEK_DO_RPP_V3_CHRONOLOGICZNY.md  
**Metodologia:** Adversarial Analysis + Fact-Checking + Legal Review

---

## PODSUMOWANIE AUDYTU

| Kategoria | Znalezione | Krytyczne | Do poprawy |
|:---|:---:|:---:|:---:|
| Błędy merytoryczne | 4 | 1 | 3 |
| Niekonsystencje dat/liczb | 3 | 0 | 3 |
| Słabe punkty argumentacji | 6 | 2 | 4 |
| Powtórzenia treści | 2 | 0 | 2 |
| Problemy z cytatami | 2 | 0 | 2 |
| Błędy formalne | 1 | 0 | 1 |

**OGÓLNA OCENA:** Dokument solidny, ale wymaga kilku poprawek przed złożeniem.

---

## I. BŁĘDY MERYTORYCZNE (KRYTYCZNE)

### 🔴 KRYTYCZNY: Błędne zastosowanie Art. 162 KK

**Lokalizacja:** Zarzut 7, linia 455

**Problem:**
> `Art. 162 KK (nieudzielenie pomocy)`

Art. 162 KK dotyczy **nieudzielenia pomocy osobie znajdującej się w położeniu grożącym bezpośrednim niebezpieczeństwem utraty życia** – wymaga BEZPOŚREDNIEGO zagrożenia życia w momencie zaniechania.

**Jak szpital to podważy:**
*"Myśli samobójcze wyrażone w wiadomościach prywatnych nie oznaczają bezpośredniego położenia grożącego utratą życia w rozumieniu Art. 162 KK. Pacjent był hospitalizowany, pod opieką personelu, nie podjął prób samobójczych."*

**Rekomendacja:** 
Zmień na **Art. 160 § 2 KK** (narażenie na niebezpieczeństwo przez osobę zobowiązaną) lub usuń kwalifikację karną, pozostawiając tylko Art. 6 UPP.

---

### ⚠️ UWAGA: Przesadzona kwalifikacja Art. 3 EKPC (tortury)

**Lokalizacja:** Zarzut 3 (drenaż), Zarzut 14 (głodzenie)

**Problem:**
Art. 3 EKPC ("nieludzkie lub poniżające traktowanie") to bardzo wysoki standard w orzecznictwie ETPCz. Wymaga **intencjonalności** lub skrajnego zaniedbania systemowego.

**Jak szpital to podważy:**
*"Drenaż wykonano z użyciem lidokainy – podjęto próbę znieczulenia. Brak jest dowodu na intencjonalne zadawanie bólu. Głodzenie nie było celowe – pacjentowi oferowano dietę szpitalną."*

**Rekomendacja:**
- Zachowaj Art. 40 Konstytucji RP (nie wymaga intencji)
- Art. 3 EKPC pozostaw jako *argumentum a fortiori*, nie jako główną podstawę
- Podkreśl **wzorzec postępowania** (drenaż 20.04 vs 30.04 – szpital WIEDZIAŁ jak zrobić prawidłowo)

---

### ⚠️ UWAGA: Niespójność w liczbie TK

**Lokalizacja:** 
- Zarzut 1, linia 187: "5 badań TK bez kontrastu doustnego"
- Tabela w liniach 178-185: pokazuje 6 badań TK

**Problem:**
Tabela zawiera 6 dat TK:
1. 03.04.2023
2. 17.04.2023
3. 25.04.2023
4. 28.04.2023
5. 08.05.2023
6. 25.05.2023

Ale jedno (25.05) miało kontrast doustny, więc "5 bez kontrastu doustnego" jest poprawne.

**Jednak:** W liniach 196 i 1027 mówisz o "5 ślepych badaniach", co jest poprawne.

**Status:** ✅ Spójne po weryfikacji, ale sprawdź czy w innych miejscach nie ma błędu.

---

### ⚠️ UWAGA: Niejasność ws. liczby drenażów

**Lokalizacja:** Różne miejsca

**Problem:**
Dokument wspomina o:
- Drenażu 20.04.2023 (bez znieczulenia)
- Drenażu 30.04.2023 (pod narkozą)

Ale później w Zarzucie 15 pytanie 15.1 wspomina o "workach TPN" – to inna procedura.

**Status:** ✅ OK, ale upewnij się że nie mieszasz terminologii.

---

## II. NIEKONSYSTENCJE DAT/LICZB

### ⚠️ Niespójność: "50 dni" vs "33 dni głodzenia"

**Lokalizacja:**
- Linia 33: "50 dni hospitalizacji w Bielsku"
- Zarzut 14: "33 dni głodzenia" (28.04-30.05)

**Wyjaśnienie:**
- Bielsko = 3 hospitalizacje (6 + 11 + 33 = **50 dni**)
- Głodzenie dotyczy tylko III hospitalizacji (33 dni)

**Rekomendacja:** Dodaj wyjaśnienie w Zarzucie 14, że obliczenia dotyczą III hospitalizacji (28.04-30.05).

---

### ⚠️ Problem: Rok 2026 w dacie dokumentu

**Lokalizacja:** Linia 5

**Problem:**
> `Data: _______________ 2026 r.`

Dokument odnosi się do zdarzeń z 2023 roku, składany jest w 2026.

**Jak szpital to podważy:**
*"Skarga złożona 3 lata po zdarzeniach – czy nie upłynął termin przedawnienia?"*

**Weryfikacja:**
- Art. 50 UPP nie ma terminu przedawnienia dla skargi do RPP
- Skarga do RPP ≠ roszczenie cywilne (gdzie termin to 3 lata od dowiedzenia się o szkodzie)

**Rekomendacja:** Rozważ dodanie zdania: *"Skarga składana jest w terminie, gdyż przepisy o RPP nie przewidują przedawnienia skargi."*

---

### ⚠️ PESEL w dokumencie

**Lokalizacja:** Linia 17

**Problem:**
> `PESEL: 01250803236`

PESEL jest **pełny i jawny** w dokumencie. Przy publikacji/udostępnianiu może to stanowić ryzyko.

**Rekomendacja:** Pozostaw do oficjalnego złożenia, ale **nigdy nie publikuj** tej wersji.

---

## III. SŁABE PUNKTY ARGUMENTACJI (RED TEAM)

### 🔶 Słaby punkt 1: Brak bezpośredniego cytatu z dokumentacji na "tortury"

**Zarzut 3** – drenaż bez znieczulenia

**Problem:**
Głównym dowodem są wiadomości Messenger. Szpital odpowie:
*"Dokumentacja medyczna wskazuje, że zastosowano znieczulenie miejscowe lidokainą. Subiektywna relacja pacjenta na Messengerze nie stanowi dowodu na brak znieczulenia."*

**Wzmocnienie argumentu:**
- ✅ Masz histopatologię (23/49105) – dowód na głębokość zabiegu
- ✅ Masz porównanie z 30.04 (narkoza) – szpital wiedział jak
- ❌ Brak karty zabiegowej z 20.04 – **TO JEST TWÓJ NAJSILNIEJSZY ARGUMENT**

**Rekomendacja:** Podkreśl bardziej BRAK dokumentacji dla 20.04 – to szpital musi wyjaśnić, dlaczego nie ma karty.

---

### 🔶 Słaby punkt 2: Łańcuch przyczynowy Bielsko → Sepsa

**Lokalizacja:** Linia 110-111, 119-120

**Problem:**
Łańcuch:
> Niedożywienie z Bielska → TPN w Krakowie → cewnik centralny → zakażenie → wstrząs

**Jak szpital to podważy:**
*"Wstrząs septyczny (24.09.2023) był spowodowany przez Staphylococcus aureus z cewnika założonego w INNYM szpitalu (Wojskowy Kraków). Nie ponosimy odpowiedzialności za powikłania leczenia w innej placówce."*

**Obrona:**
- Argumentuj, że **gdyby Bielsko prawidłowo żywiło pacjenta**, cewnik centralny nie byłby potrzebny
- Podkreśl, że Bielsko wypisało pacjenta **niedożywionego** (BMI ~16)

**Rekomendacja:** Wzmocnij sformułowanie łańcucha przyczynowego – "błędy Bielska stworzyły warunki wymagające interwencji, która doprowadziła do sepsy".

---

### 🔶 Słaby punkt 3: Dowody Messenger = nieoficjalne

**Problem ogólny:**

Prawie wszystkie cytaty pochodzą z Messengera. Szpital może argumentować:
*"Prywatne rozmowy pacjenta nie stanowią wiarygodnego dowodu medycznego. Mogą zawierać przesadę, emocje, nieścisłości."*

**Obrona:**
- Messenger to **zapis w czasie rzeczywistym** – nie pisany post-factum
- Wiele wiadomości zawiera **detale kliniczne** (temperatury, procedury)
- Porównaj z BRAKAMI w dokumentacji szpitalnej

**Rekomendacja:** W oświadczeniu (VII) dodaj zdanie o gotowości do złożenia eksportu Messengera jako dowodu elektronicznego.

---

### 🔶 Słaby punkt 4: "20% szansy na zgon" – źródło?

**Lokalizacja:** Zarzut 13, linia 766

**Problem:**
Cytat:
> *„20% szansy na zgon"*

Kto to powiedział? Prof. Richter? Kraków?

**Jak szpital to podważy:**
*"Brak dokumentacji źródłowej dla tego twierdzenia. Pacjent może przesadzać."*

**Rekomendacja:** Jeśli masz nagranie rozmowy z prof. Richterem lub zapis – wskaż to. Jeśli nie, zmień na "wg oceny ośrodka referencyjnego, ryzyko operacji było znacząco podwyższone".

---

### 🔶 Słaby punkt 5: Diagnoza F43.2 a PTSD

**Lokalizacja:** Linie 136-144, 148

**Problem:**
- F43.2 = Zaburzenia adaptacyjne (**NIE PTSD**)
- W dokumencie używasz terminu "PTSD" w nagłówku "JATROGENNE PTSD"

**Jak szpital to podważy:**
*"Pacjent nie ma diagnozy PTSD (F43.1). F43.2 to zaburzenia adaptacyjne – mniej poważna diagnoza."*

**Rekomendacja:** 
- Zmień "JATROGENNE PTSD" na "JATROGENNA TRAUMA PSYCHICZNA" lub "ZABURZENIA ADAPTACYJNE"
- Lub wyjaśnij, że F43.2 objawia się podobnie do PTSD

---

### 🔶 Słaby punkt 6: Brak opinii biegłego na żywienie

**Zarzut 14** – głodzenie

**Problem:**
Obliczenia kaloryczne są szczegółowe, ale oparte na:
- Standardowych tabelach (Harris-Benedict)
- Relacji pacjenta
- Braku dokumentacji szpitalnej

**Jak szpital to podważy:**
*"Szpital prowadził dokumentację żywieniową zgodnie z przepisami. Pacjent otrzymywał odpowiednie posiłki. Obliczenia skarżącego są spekulatywne."*

**Rekomendacja:** 
Twój disclaimer (linia 933-934) jest dobry – zachowaj go. Podkreśl, że **BRAK kart żywieniowych** w dokumentacji to wina szpitala.

---

## IV. POWTÓRZENIA TREŚCI

### ⚠️ Powtórzenie 1: Wnioski o biegłych

**Lokalizacja:**
- Każdy zarzut kończy się "WNIOSEK O OCENĘ BIEGŁEGO"
- Sekcja V (Uzasadnienie wniosku o biegłych) powtarza te same tematy

**Rekomendacja:** To akceptowalne – powtórzenie wzmacnia przekaz.

---

### ⚠️ Powtórzenie 2: Pytania 1.5 i 3.5 częściowo się pokrywają

**Lokalizacja:**
- Pytanie 1.5: brak TK z kontrastem przed drenażem 20.04
- Pytanie 3.4: brak Karty Zabiegowej dla drenażu 20.04

**Rekomendacja:** OK – różne aspekty tego samego zdarzenia.

---

## V. PROBLEMY Z CYTATAMI

### ⚠️ Brak źródła dla cytatu ordynatora

**Lokalizacja:** Linia 778

**Problem:**
> `Ordynator: *„Sam bym swojego syna tu nie leczył w tej sytuacji\"*`

Skąd ten cytat? Messenger? Nagranie?

**Rekomendacja:** Wskaż źródło (data, kontekst). Jeśli to z rozmowy ustnej – usuń lub zmień na "wg relacji pacjenta/rodziny".

---

### ⚠️ Cytat Prof. Richtera – data niepewna

**Lokalizacja:** Linia 769

**Problem:**
> `Cytat z prywatnej wizyty u prof. Richtera (~01.06.2023)`

Znak "~" sugeruje niepewność. 

**Rekomendacja:** Jeśli masz dokładną datę – wstaw ją. Jeśli nie – zostaw z "~".

---

## VI. BŁĘDY FORMALNE

### ⚠️ Brak daty złożenia

**Lokalizacja:** Linia 1060

**Problem:**
> `Data złożenia: _______________`

**Rekomendacja:** Uzupełnij przed wysłaniem.

---

## VII. WERYFIKACJA PRZEPISÓW PRAWNYCH

| Przepis | Użycie | Poprawność |
|:---|:---|:---:|
| Art. 50-52 UPP | Osnowa skargi | ✅ OK |
| Art. 6 UPP | Prawo do świadczeń | ✅ OK |
| Art. 8 UPP | Należyta staranność | ✅ OK |
| Art. 20 UPP | Godność, intymność | ✅ OK |
| Art. 20a UPP | Leczenie bólu | ✅ OK |
| Art. 23-26 UPP | Dokumentacja | ✅ OK |
| Art. 160 KK | Narażenie życia | ✅ OK (§2 dla gwarantów) |
| Art. 162 KK | Nieudzielenie pomocy | ⚠️ Do zmiany (Zarzut 7) |
| Art. 165 KK | Zagrożenie wielu osób | ✅ OK (ESBL+ bez izolacji) |
| Art. 271 KK | Poświadczenie nieprawdy | ✅ OK |
| Art. 286 KK | Wyłudzenie | ⚠️ Zachowaj ostrożność - trudne do udowodnienia |
| Art. 157 KK | Rozstrój zdrowia | ✅ OK |
| Art. 3 EKPC | Tortury | ⚠️ Wysoki standard - używaj ostrożnie |
| Art. 40 Konstytucji | Zakaz tortur | ✅ OK |
| Art. 445 KC | Zadośćuczynienie | ✅ OK |
| Wytyczne ECCO | Standard leczenia Crohna | ✅ OK |
| Wytyczne ESPEN | Żywienie kliniczne | ✅ OK |
| Wytyczne CDC/ECDC | Izolacja patogenów | ✅ OK |

---

## VIII. REKOMENDACJE PRZED ZŁOŻENIEM

### KRYTYCZNE (musi być zmienione):

1. **Zmień Art. 162 KK → Art. 160 § 2 KK** w Zarzucie 7 (psycholog)

### ZALECANE (wzmocni argumentację):

2. Zmień "JATROGENNE PTSD" → "JATROGENNA TRAUMA PSYCHICZNA (F43.2)"
3. Wskaź źródło cytatu ordynatora ("Sam bym syna...")
4. Wzmocnij łańcuch przyczynowy Bielsko → Sepsa
5. Rozważ usunięcie Art. 286 KK (wyłudzenie) – trudne do udowodnienia, może osłabić wiarygodność

### DROBNE (opcjonalne):

6. Dodaj zdanie o braku przedawnienia skargi do RPP
7. Uzupełnij datę złożenia

---

## IX. PODSUMOWANIE

**OGÓLNA OCENA DOKUMENTU:** ⭐⭐⭐⭐ (4/5)

Dokument jest **solidny, szczegółowy i dobrze udokumentowany**. Zawiera:
- ✅ 15 zarzutów w kolejności chronologicznej
- ✅ 75 szczegółowych pytań do biegłych
- ✅ Liczne cytaty i dowody
- ✅ Poprawne kwalifikacje prawne (z drobnymi wyjątkami)
- ✅ Jasny łańcuch przyczynowo-skutkowy

**Główne ryzyko:** Szpital będzie atakował:
1. Wiarygodność dowodów z Messengera
2. Łańcuch przyczynowy do sepsy (inny szpital)
3. Wysokie standardy Art. 3 EKPC

**Rekomendacja końcowa:** Po poprawkach (zwłaszcza Art. 162 KK) dokument jest gotowy do złożenia.

---

**Przygotował:** System Antigravity (Red Team Analysis)
