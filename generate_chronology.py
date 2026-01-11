
import os
import re

SOURCE_DIR = r"c:\Users\micha\.gemini\antigravity\PROJEKT POZEW\raporty_dzien_po_dniu"
OUTPUT_FILE = r"c:\Users\micha\.gemini\antigravity\PROJEKT POZEW\CHRONOLOGIA_CALOSCIOWA.md"

HEADER = """# 📅 CHRONOLOGIA CAŁOŚCIOWA (02.04 - 30.05.2023)

**Legenda Wagi:**
*   🔴 **KRYTYCZNE:** Zagrożenie życia, błędy medyczne, zabiegi, zakażenia.
*   🟡 **WAŻNE:** Cierpienie, ból, głód, procedury.
*   ⚪ **RUTYNA:** Dzień szpitalny bez incydentów.

| Data | Dzień | Kluczowe Wydarzenie | Waga |
|:---|:---|:---|:---:|
"""

def generate():
    files = sorted([f for f in os.listdir(SOURCE_DIR) if f.endswith(".md")])
    
    rows = []
    
    for filename in files:
        # Match YYYY-MM-DD
        match = re.search(r"(\d{4})-(\d{2})-(\d{2})", filename)
        if match:
            date_str = f"{match.group(3)}.{match.group(2)}"
            path = os.path.join(SOURCE_DIR, filename)
            
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Day of week
            first_line = content.splitlines()[0] if content else ""
            day_match = re.search(r"\((.*?)\)", first_line)
            day_of_week = day_match.group(1) if day_match else "-"
            
            # Status
            status_match = re.search(r"## .* Status: (.*)", content)
            status = status_match.group(1).strip() if status_match else "Brak statusu"
            
            # Weight
            weight = "⚪"
            critical_keywords = [
                "SEPSA", "ZAGROŻENIE", "BŁĄD", "ZANIEDBANIE", "NARKOZA", "OPERACJA", 
                "TK ", "TOMOGRAFIA", "BAKTERIA", "ESBL", "ROPIEŃ", "PRZETOKA", 
                "DRENAŻ", "TRAUMA", "PO_NARKOZYM", "UCIECZKA", "RUTYNA_ZLE", "IZOLATKA"
            ]
            important_keywords = [
                "BÓL", "WYMIOTY", "GŁÓD", "DIETA", "KROPLÓWKA", "WENFLON", "SOR", 
                "Szpital", "Lekarz", "ZUPA_MLECZNA", "KABANOSY"
            ]
            
            # Check critical
            if any(kw in content for kw in critical_keywords):
                weight = "🔴"
            # Check important if not critical
            elif any(kw in content for kw in important_keywords):
                weight = "🟡"
                
            rows.append(f"| **{date_str}** | {day_of_week} | {status} | {weight} |")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n".join(rows) + "\n")
    
    print(f"Wygenerowano plik: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate()
