import os
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"C:\Users\micha\.gemini\antigravity\PROJEKT POZEW\dokumentacja wewnetrzna")
OUTPUT_FILE = r"C:\Users\micha\.gemini\antigravity\PROJEKT POZEW\INWENTARYZACJA_DOKUMENTACJI_PELNA.md"

def get_hosp_period(filename):
    # Try to extract date
    try:
        # Formats: 2023.04.02, 2023-04-28
        date_str = filename[:10].replace('.', '-').replace('_', '-')
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        
        if datetime(2023, 4, 1) <= date_obj <= datetime(2023, 4, 10):
            return "Hospitalizacja I (04.2023)"
        elif datetime(2023, 4, 17) <= date_obj <= datetime(2023, 6, 15):
            return "Hospitalizacja II (04-05.2023)"
        else:
            return "Inny okres"
    except:
        return "Nieznany okres"

def scan_files():
    inventory = []
    
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            path = Path(root) / file
            rel_path = path.relative_to(BASE_DIR)
            size_kb = os.path.getsize(path) / 1024
            
            period = get_hosp_period(file)
            if period == "Nieznany okres":
                 # Try folder name
                 period = get_hosp_period(path.parent.name)
            
            inventory.append({
                "file": file,
                "path": str(rel_path),
                "size": size_kb,
                "period": period,
                "type": path.suffix.lower()
            })
            
    return inventory

def generate_report(inventory):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# 📂 PEŁNA INWENTARYZACJA DOKUMENTACJI WEWNĘTRZNEJ\n\n")
        f.write(f"Data generowania: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        
        # Summary
        total_files = len(inventory)
        total_size = sum(x['size'] for x in inventory) / 1024 # MB
        f.write(f"**Łącznie plików:** {total_files}\n")
        f.write(f"**Rozmiar całkowity:** {total_size:.2f} MB\n\n")
        
        # Group by Period
        periods = sorted(list(set(x['period'] for x in inventory)))
        
        for p in periods:
            f.write(f"## {p}\n")
            period_files = [x for x in inventory if x['period'] == p]
            f.write("| Plik | Ścieżka | Rozmiar (KB) | Typ |\n")
            f.write("|---|---|---|---|\n")
            for item in sorted(period_files, key=lambda x: x['path']):
                 f.write(f"| `{item['file']}` | `{item['path']}` | {item['size']:.1f} | {item['type']} |\n")
            f.write("\n")

if __name__ == "__main__":
    print("Skanowanie dokumentacji...")
    data = scan_files()
    generate_report(data)
    print(f"Raport zapisany w: {OUTPUT_FILE}")
