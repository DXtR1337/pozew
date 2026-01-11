from pathlib import Path

FILE_PATH = Path(r"C:\Users\micha\.gemini\antigravity\PROJEKT POZEW\VISUAL_FORENSICS_FULL_TIMELINE.md")

DESCRIPTIONS = {
    "2023-04-06": "Stan dobry, I hospitalizacja, jedzenie szpitalne",
    "2023-04-07": "Noc przed wypisem, zmęczenie",
    "2023-04-09": "Pobyt w domu, selfie",
    "2023-04-11": "Pobyt w domu, pogorszenie wyglądu (bladość)",
    "2023-04-20": "Dren założony prawidłowo (Baseline leczenia)",
    "2023-04-22": "Stan stabilny, wygląd dobry (Baseline fizyczny)",
    "2023-04-24": "Początki zmęczenia szpitalnego",
    "2023-04-27": "Widoczny wyciek z rany (ignorowany)",
    "2023-05-10": "Powrót do diety, selfie (zmęczenie)",
    "2023-05-14": "AGONIA: Otwarta rana ('dziura'), cierpienie bólowe",
    "2023-05-15": "Stan po kryzysie bólowym",
    "2023-05-16": "Rutyna szpitalna, selfie",
    "2023-05-18": "Ślady po szyciu drenu 'na żywca', stan zapalny",
    "2023-05-20": "Obraz wyniszczenia fizycznego i psychicznego",
    "2023-05-21": "Masywny wyciek kałowy (ignorowany przez personel)",
    "2023-05-23": "CIĄGŁOŚĆ: Wyciek kałowy utrzymuje się, brak reakcji",
    "2023-05-25": "KRYZYS: Niezdiagnozowana przetoka, stan septyczny",
    "2023-06-04": "Po wypisie: Rana NIEZAGOJONA (otwór w brzuchu)",
    "2023-06-08": "Dom: Dalsze cierpienie, próby rekonwalescencji"
}

def main():
    content = FILE_PATH.read_text(encoding="utf-8")
    lines = content.splitlines()
    new_lines = []
    
    for line in lines:
        updated = False
        for date_key, desc in DESCRIPTIONS.items():
            if f"| **{date_key}** |" in line:
                # Replace "[ ] Do analizy" with description
                new_line = line.replace("[ ] Do analizy", f"✅ {desc}")
                new_lines.append(new_line)
                updated = True
                break
        if not updated:
            new_lines.append(line)
            
    FILE_PATH.write_text("\n".join(new_lines), encoding="utf-8")
    print("Timeline updated successfully.")

if __name__ == "__main__":
    main()
