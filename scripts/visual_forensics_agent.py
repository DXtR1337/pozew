"""
FORENSIC DEEP DIVE - Visual Forensics Agent
Weryfikator Zdjęć: Analiza metadanych EXIF i zestawienie z dokumentacją medyczną.

Cel: Udowodnić sprzeczność między stanem wizualnym rany a opisem "rana spokojna".
"""

import os
import re
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Dict
from collections import defaultdict

# Próba importu PIL dla EXIF (opcjonalnie)
try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("⚠️ PIL/Pillow nie zainstalowany - metadane EXIF niedostępne")

@dataclass
class ImageEvidence:
    filepath: Path
    filename: str
    date_taken: Optional[datetime]
    date_source: str  # EXIF, FILENAME, MODIFIED
    file_size_kb: float
    description: str  # Do uzupełnienia przez vision model lub ręcznie
    
@dataclass
class DocumentEntry:
    date: datetime
    content: str
    source: str

def extract_date_from_exif(filepath: Path) -> Optional[datetime]:
    """Wyciągnij datę z metadanych EXIF"""
    if not HAS_PIL:
        return None
    
    try:
        image = Image.open(filepath)
        exif_data = image._getexif()
        
        if exif_data:
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag in ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized']:
                    # Format: "2023:04:28 14:30:00"
                    try:
                        return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                    except ValueError:
                        continue
    except Exception:
        pass
    
    return None

def extract_date_from_filename(filename: str) -> Optional[datetime]:
    """Wyciągnij datę z nazwy pliku"""
    # Różne wzorce dat w nazwach plików
    patterns = [
        (r'(\d{4}-\d{2}-\d{2})\s*(\d{2}\.\d{2})?', "%Y-%m-%d"),  # 2023-04-28 19.19
        (r'(\d{4})(\d{2})(\d{2})', None),  # 20230428
        (r'Screenshot_(\d{4})-(\d{2})-(\d{2})', None),  # Screenshot_2025-12-27
        (r'(\d{2})\.(\d{2})\.(\d{4})', None),  # 28.04.2023
    ]
    
    # Wzorzec główny
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})', filename)
    if match:
        try:
            return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            pass
    
    # Wzorzec z kropkami
    match = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', filename)
    if match:
        try:
            return datetime(int(match.group(3)), int(match.group(2)), int(match.group(1)))
        except ValueError:
            pass
    
    return None

def extract_date_from_modified(filepath: Path) -> Optional[datetime]:
    """Wyciągnij datę z czasu modyfikacji pliku"""
    try:
        mtime = os.path.getmtime(filepath)
        return datetime.fromtimestamp(mtime)
    except:
        return None

def scan_images(base_path: Path) -> List[ImageEvidence]:
    """Przeskanuj wszystkie obrazy w projekcie"""
    images = []
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    
    # Foldery do skanowania
    scan_dirs = [
        base_path / "screenyu",
        base_path / "skany_dokumentacji_2023_04_28",
        base_path / "dokumentacja wewnetrzna" / "AnyPDFtoJPG",
        base_path / "NOWE SCREENY!",
        base_path / "wpisy 1 BB pojedyncze skany jpg",
        base_path / "jeszce nowsze",
        base_path / "ZDJECIA Z HOSPITALIZACJI przed i po w trakcie",
    ]
    
    # Dodaj root directory też
    scan_dirs.append(base_path)
    
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
            
        for f in scan_dir.glob("*"):
            if f.is_file() and f.suffix.lower() in image_extensions:
                # Wyciągnij datę różnymi metodami
                date = extract_date_from_exif(f)
                date_source = "EXIF"
                
                if not date:
                    date = extract_date_from_filename(f.name)
                    date_source = "FILENAME"
                
                if not date:
                    date = extract_date_from_modified(f)
                    date_source = "MODIFIED"
                
                # Rozmiar pliku
                size_kb = f.stat().st_size / 1024
                
                images.append(ImageEvidence(
                    filepath=f,
                    filename=f.name,
                    date_taken=date,
                    date_source=date_source,
                    file_size_kb=size_kb,
                    description="[DO ANALIZY WIZUALNEJ]"
                ))
    
    return images

def load_documentation_entries(base_path: Path) -> List[DocumentEntry]:
    """Wczytaj wpisy z dokumentacji medycznej (raporty dzienne)"""
    entries = []
    reports_dir = base_path / "raporty_dzien_po_dniu"
    
    if not reports_dir.exists():
        return entries
    
    # Szukaj fraz opisujących stan rany
    wound_phrases = [
        'rana', 'gojenie', 'opatrunek', 'spokojna', 'czysta', 'sucha',
        'stan dobry', 'bez zmian', 'prawidłowy'
    ]
    
    for f in reports_dir.glob("*.md"):
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', f.name)
        if not date_match:
            continue
        
        try:
            date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
        except ValueError:
            continue
        
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Wyciągnij fragmenty o ranie
        for phrase in wound_phrases:
            if phrase.lower() in content.lower():
                entries.append(DocumentEntry(
                    date=date,
                    content=content[:500],
                    source=str(f)
                ))
                break
    
    return entries

def generate_visual_forensics_report(images: List[ImageEvidence], 
                                     doc_entries: List[DocumentEntry],
                                     output_path: Path):
    """Generuj raport Visual Forensics"""
    
    # Grupuj obrazy po datach
    by_date = defaultdict(list)
    for img in images:
        if img.date_taken:
            by_date[img.date_taken.date()].append(img)
    
    # Grupuj dokumentację po datach
    docs_by_date = defaultdict(list)
    for doc in doc_entries:
        docs_by_date[doc.date.date()].append(doc)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 📸 RAPORT VISUAL FORENSICS: Zdjęcia vs Dokumentacja\n\n")
        f.write("**Cel:** Zestawienie wizualnego stanu rany ze zdjęć z opisami w dokumentacji medycznej.\n\n")
        f.write(f"**Przeanalizowano obrazów:** {len(images)}\n")
        f.write(f"**Obrazów z datą:** {sum(1 for img in images if img.date_taken)}\n\n")
        
        f.write("> [!IMPORTANT]\n")
        f.write("> Ten raport wymaga ręcznej analizy wizualnej zdjęć i porównania z opisami.\n")
        f.write("> Jeśli zdjęcie pokazuje ropę/martwicę, a dokumentacja mówi 'rana spokojna' - to DOWÓD FAŁSZERSTWA.\n\n")
        
        f.write("---\n\n")
        
        # Statystyki źródeł dat
        f.write("## 📊 Źródła dat obrazów\n\n")
        source_counts = defaultdict(int)
        for img in images:
            source_counts[img.date_source] += 1
        
        f.write("| Źródło daty | Liczba |\n")
        f.write("|-------------|--------|\n")
        for src, count in sorted(source_counts.items(), key=lambda x: -x[1]):
            f.write(f"| {src} | {count} |\n")
        f.write("\n---\n\n")
        
        # Zestawienie po datach (z okresu hospitalizacji)
        f.write("## 🗓️ Obrazy z okresu III hospitalizacji (17.04-30.05.2023)\n\n")
        
        hosp_dates = [d for d in sorted(by_date.keys()) 
                     if datetime(2023, 4, 17).date() <= d <= datetime(2023, 5, 30).date()]
        
        if not hosp_dates:
            f.write("⚠️ Brak obrazów z datami w okresie hospitalizacji.\n\n")
            f.write("**Znalezione daty:**\n")
            for d in sorted(by_date.keys())[:10]:
                f.write(f"- {d}: {len(by_date[d])} obrazów\n")
        else:
            for date in hosp_dates:
                day_images = by_date[date]
                day_docs = docs_by_date.get(date, [])
                
                f.write(f"### 📆 {date.strftime('%Y-%m-%d')}\n\n")
                f.write(f"**Obrazów:** {len(day_images)}\n\n")
                
                f.write("| Plik | Źródło daty | Rozmiar | Do analizy |\n")
                f.write("|------|-------------|---------|------------|\n")
                for img in day_images[:10]:
                    f.write(f"| `{img.filename[:40]}` | {img.date_source} | {img.file_size_kb:.0f} KB | 🔍 |\n")
                
                if day_docs:
                    f.write("\n**Dokumentacja z tego dnia:**\n")
                    for doc in day_docs:
                        f.write(f"> {doc.content[:150]}...\n\n")
                
                f.write("---\n\n")
        
        # Lista wszystkich obrazów do analizy
        f.write("## 📁 Pełna lista obrazów\n\n")
        
        # Grupuj po folderach
        by_folder = defaultdict(list)
        for img in images:
            folder = img.filepath.parent.name
            by_folder[folder].append(img)
        
        for folder, folder_images in sorted(by_folder.items(), key=lambda x: -len(x[1])):
            f.write(f"### 📂 {folder}/ ({len(folder_images)} plików)\n\n")
            
            for img in sorted(folder_images, key=lambda x: x.date_taken or datetime.min)[:5]:
                date_str = img.date_taken.strftime('%Y-%m-%d %H:%M') if img.date_taken else "BRAK DATY"
                f.write(f"- `{img.filename}` ({date_str}, {img.date_source})\n")
            
            if len(folder_images) > 5:
                f.write(f"- ... i {len(folder_images) - 5} więcej\n")
            f.write("\n")
        
        # Instrukcje dla użytkownika
        f.write("## 🎯 NEXT STEPS\n\n")
        f.write("1. **Przejrzyj zdjęcia ran** z okresu hospitalizacji\n")
        f.write("2. **Opisz stan wizualny** (ropa, zaczerwienienie, martwica, brudny opatrunek)\n")
        f.write("3. **Porównaj z dokumentacją** - szukaj fraz 'rana spokojna', 'gojenie prawidłowe'\n")
        f.write("4. **Oznacz sprzeczności** jako [DOWÓD FAŁSZERSTWA]\n\n")
        f.write("**Do analizy przez Vision Model:**\n")
        f.write("```\n")
        f.write("Opisz stan rany na tym zdjęciu: \n")
        f.write("- Czy widoczna jest ropa/wysięk?\n")
        f.write("- Czy jest zaczerwienienie/obrzęk?\n")
        f.write("- Czy opatrunek jest czysty czy brudny?\n")
        f.write("- Czy widoczne są oznaki zakażenia?\n")
        f.write("```\n")
    
    print(f"✅ Raport Visual Forensics zapisany: {output_path}")

def main():
    base_path = Path(r"C:\Users\micha\.gemini\antigravity\PROJEKT POZEW")
    
    print("📸 AGENT VISUAL FORENSICS - Weryfikator Zdjęć")
    print("=" * 60)
    
    print("\n🔍 Skanowanie obrazów...")
    images = scan_images(base_path)
    print(f"   Znaleziono: {len(images)} obrazów")
    
    with_date = sum(1 for img in images if img.date_taken)
    print(f"   Z datą: {with_date}")
    
    print("\n📋 Wczytywanie dokumentacji...")
    doc_entries = load_documentation_entries(base_path)
    print(f"   Wpisów o ranach: {len(doc_entries)}")
    
    # Generuj raport
    output_path = base_path / "RAPORT_VISUAL_FORENSICS.md"
    generate_visual_forensics_report(images, doc_entries, output_path)
    
    print("\n" + "=" * 60)
    print("✅ ZAKOŃCZONO")
    
    # Jeśli brak PIL, pokaż instrukcję instalacji
    if not HAS_PIL:
        print("\n💡 Aby odczytać metadane EXIF, zainstaluj Pillow:")
        print("   pip install Pillow")

if __name__ == "__main__":
    main()
