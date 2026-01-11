import os
import re
from pathlib import Path
from datetime import datetime
import json

# Paths
BASE_DIR = Path(r"C:\Users\micha\.gemini\antigravity\PROJEKT POZEW")
IMG_DIR = BASE_DIR / "ZDJECIA Z HOSPITALIZACJI przed i po w trakcie"
REPORT_DIR = BASE_DIR / "raporty_dzien_po_dniu"
OUTPUT_FILE = BASE_DIR / "VISUAL_FORENSICS_FULL_TIMELINE.md"

def get_date_from_filename(filename):
    # Match 20230514 style
    match = re.search(r"(2023\d{2}\d{2})", filename)
    if match:
        return datetime.strptime(match.group(1), "%Y%m%d").date()
    return None

def get_report_context(date_obj):
    date_str = date_obj.strftime("%Y-%m-%d")
    # Find matching report
    for report_file in REPORT_DIR.glob("*.md"):
        if date_str in report_file.name:
            try:
                content = report_file.read_text(encoding="utf-8")
                # Extract header context (first few lines or "Status")
                lines = content.splitlines()
                status = "Brak statusu"
                title = report_file.name
                
                for line in lines:
                    if "## 📍 Status:" in line:
                        status = line.replace("## 📍 Status:", "").strip()
                        break
                return f"**Raport:** {title}\n**Status:** {status}"
            except Exception as e:
                return f"Error reading report: {e}"
    return "Brak raportu dziennego dla tej daty."

def main():
    print("Ralph Forensic Analyst: Building Visual Timeline...")
    
    # 1. Scan images
    images = []
    for img_path in IMG_DIR.glob("*"):
        if img_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
            img_date = get_date_from_filename(img_path.name)
            if img_date:
                images.append({
                    "path": img_path,
                    "name": img_path.name,
                    "date": img_date,
                    "size": os.path.getsize(img_path)
                })
    
    # Sort by date
    images.sort(key=lambda x: x["date"])
    
    # 2. Build Markdown
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# 📸 PEŁNA OŚ CZASU DOWODÓW WIZUALNYCH (Ralph Auto-Gen)\n\n")
        f.write(f"Wygenerowano: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Liczba zdjęć: {len(images)}\n\n")
        f.write("| Data | Zdjęcie | Kontekst Medyczny (Raport Dzienny) | Opis Wizualny (Do uzupełnienia) |\n")
        f.write("|---|---|---|---|\n")
        
        current_date = None
        
        for img in images:
            date_display = img["date"].strftime("%Y-%m-%d")
            
            # Grouping visually by date
            if img["date"] != current_date:
                context = get_report_context(img["date"])
                current_date = img["date"]
            else:
                context = "*(te same wydarzenia)*"
            
            # Check if it's a "selfie" (based on filename heuristic check later manual)
            # Just listing file for now
            
            f.write(f"| **{date_display}** | `{img['name']}`<br>({img['size']/1024:.0f} KB) | {context} | [ ] Do analizy |\n")

    print(f"Timeline generated at: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
