"""
TIMELINE EXTRACTOR - Oś Czasu "Co do Minuty"
Ekstrakcja i unifikacja timestampów z różnych źródeł dla sprawy medycznej.
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

@dataclass
class TimelineEvent:
    """Pojedyncze zdarzenie na osi czasu"""
    timestamp: datetime
    source: str  # MESSENGER, WHATSAPP, DOKUMENTACJA, RAPORT
    sender: str
    content: str
    file_origin: str
    is_medical: bool = False
    is_discrepancy: bool = False
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "sender": self.sender,
            "content": self.content,
            "file_origin": self.file_origin,
            "is_medical": self.is_medical,
            "is_discrepancy": self.is_discrepancy
        }

# Słowa kluczowe medyczne do wykrycia
MEDICAL_KEYWORDS = [
    "ból", "boli", "szpital", "lekarz", "operacja", "zabieg", "drenaż", "drenaz",
    "gorączka", "goraczka", "ropień", "ropien", "antybiotyk", "kroplówka", "kroplowka",
    "pielęgniarka", "pielegniarka", "ordynator", "diagnoza", "badanie", "wynik",
    "tomografia", "TK", "USG", "krew", "posiew", "bakteria", "zakażenie", "zakazenie",
    "rana", "opatrunek", "worek", "stomia", "jelito", "Crohn", "IBD",
    "mdleje", "mdleję", "wymiotuje", "wymiotuję", "gorączka", "temperatura",
    "nie śpię", "nie spie", "nie mogę spać", "umrę", "umre", "umieram",
    "głód", "glod", "głodny", "glodny", "jedzenie", "dieta", "kisiel",
    "izolacja", "izolatka", "E.coli", "Ecoli", "sepsa",
    "na żywca", "na zywca", "bez znieczulenia", "boli mnie"
]

# Wzorce sugerujące stan "dobry" w dokumentacji
DOCUMENTATION_GOOD_STATE = [
    "stan dobry", "pacjent stabilny", "bez dolegliwości", "samopoczucie dobre",
    "prawidłowe odżywianie", "NRS 0", "żywienie prawidłowe"
]

def is_medical_content(text: str) -> bool:
    """Sprawdza czy treść zawiera słowa kluczowe medyczne"""
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in MEDICAL_KEYWORDS)

def parse_messenger_file(filepath: Path) -> List[TimelineEvent]:
    """Parsuje plik z extracted_days (format tabelaryczny)"""
    events = []
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filepath.name)
    if not date_match:
        return events
    
    date_str = date_match.group(1)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse table rows: | Godz | Nadawca | Tresc | Watek |
    pattern = r'\|\s*(\d{2}:\d{2}:\d{2})\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|'
    matches = re.findall(pattern, content)
    
    for time_str, sender, text, thread in matches:
        try:
            timestamp = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
            text = text.strip()
            sender = sender.strip()
            
            if text in ["[No text content]", "[Photo: 1]", "[Sticker]"]:
                continue  # Skip non-text
                
            event = TimelineEvent(
                timestamp=timestamp,
                source="MESSENGER",
                sender=sender,
                content=text[:200],  # Truncate long messages
                file_origin=str(filepath),
                is_medical=is_medical_content(text)
            )
            events.append(event)
        except ValueError:
            continue
    
    return events

def parse_whatsapp_file(filepath: Path) -> List[TimelineEvent]:
    """Parsuje plik WhatsApp (format: DD.MM.YYYY, HH:MM - Sender: Message)"""
    events = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # WhatsApp format: 20.04.2023, 14:32 - Mama: Treść wiadomości
    pattern = r'(\d{1,2}\.\d{1,2}\.\d{4}),\s*(\d{1,2}:\d{2})\s*-\s*([^:]+):\s*(.+)'
    matches = re.findall(pattern, content)
    
    for date_str, time_str, sender, text in matches:
        try:
            # Parse DD.MM.YYYY format
            timestamp = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")
            
            # Filter to 2023 only (relevant period)
            if timestamp.year != 2023:
                continue
            
            # Skip media placeholders
            if 'Pominięto multimedia' in text or 'załączony plik' in text:
                continue
            
            event = TimelineEvent(
                timestamp=timestamp,
                source="WHATSAPP",
                sender=sender.strip(),
                content=text.strip()[:200],
                file_origin=str(filepath),
                is_medical=is_medical_content(text)
            )
            events.append(event)
        except ValueError:
            continue
    
    return events

def parse_daily_report(filepath: Path) -> List[TimelineEvent]:
    """Parsuje raport dzienny szukając wzmianek o czasie i stanie pacjenta"""
    events = []
    
    date_match = re.search(r'(\d{2})_(\d{4})-(\d{2})-(\d{2})', filepath.name)
    if not date_match:
        return events
    
    date_str = f"{date_match.group(2)}-{date_match.group(3)}-{date_match.group(4)}"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for time patterns in the report
    time_patterns = re.findall(r'(?:o\s*)?(\d{1,2}:\d{2})(?:\s*[-–]\s*)?([^|\n]{10,100})', content)
    
    for time_str, text in time_patterns:
        try:
            # Add leading zero if needed
            if len(time_str.split(':')[0]) == 1:
                time_str = '0' + time_str
            timestamp = datetime.strptime(f"{date_str} {time_str}:00", "%Y-%m-%d %H:%M:%S")
            
            event = TimelineEvent(
                timestamp=timestamp,
                source="RAPORT_DZIENNY",
                sender="Pacjent/Raport",
                content=text.strip()[:200],
                file_origin=str(filepath),
                is_medical=True
            )
            events.append(event)
        except ValueError:
            continue
    
    return events

def detect_discrepancies(events: List[TimelineEvent]) -> List[Tuple[TimelineEvent, TimelineEvent, str]]:
    """
    Wykrywa rozbieżności między źródłami:
    - Pacjent zgłasza ból, a dokumentacja mówi "stan dobry"
    - Brak interwencji po zgłoszeniu krytycznym
    """
    discrepancies = []
    
    # Group by date
    by_date = defaultdict(list)
    for e in events:
        by_date[e.timestamp.date()].append(e)
    
    for date, day_events in by_date.items():
        # Sort by time
        day_events.sort(key=lambda x: x.timestamp)
        
        # Find patient complaints
        patient_complaints = [e for e in day_events 
                           if e.is_medical and 
                           any(kw in e.content.lower() for kw in ['ból', 'boli', 'mdleje', 'umrę', 'gorączka'])]
        
        # Find documentation entries
        doc_entries = [e for e in day_events 
                      if e.source in ['DOKUMENTACJA', 'RAPORT_DZIENNY'] and 
                      any(good in e.content.lower() for good in ['dobry', 'stabilny', 'prawidłow'])]
        
        for complaint in patient_complaints:
            for doc in doc_entries:
                # Check if documentation says "good" within 2 hours of complaint
                time_diff = abs((doc.timestamp - complaint.timestamp).total_seconds() / 3600)
                if time_diff <= 2:
                    discrepancies.append((
                        complaint,
                        doc,
                        f"ROZBIEŻNOŚĆ: Pacjent zgłosił '{complaint.content[:50]}...' o {complaint.timestamp.strftime('%H:%M')}, "
                        f"ale dokumentacja {time_diff:.1f}h później: '{doc.content[:50]}...'"
                    ))
                    complaint.is_discrepancy = True
                    doc.is_discrepancy = True
    
    return discrepancies

def generate_timeline_report(events: List[TimelineEvent], discrepancies: List, output_path: Path):
    """Generuje raport markdown z osią czasu"""
    
    # Sort all events
    events.sort(key=lambda x: x.timestamp)
    
    # Filter to medical events only for main report
    medical_events = [e for e in events if e.is_medical]
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 🕐 OŚ CZASU - CO DO MINUTY\n\n")
        f.write("Zunifikowana oś czasu z wszystkich źródeł komunikacji.\n\n")
        f.write(f"**Źródła:** Messenger, WhatsApp, Raporty dzienne\n")
        f.write(f"**Zakres dat:** {events[0].timestamp.date()} - {events[-1].timestamp.date()}\n")
        f.write(f"**Wszystkich zdarzeń:** {len(events)}\n")
        f.write(f"**Zdarzeń medycznych:** {len(medical_events)}\n")
        f.write(f"**Wykrytych rozbieżności:** {len(discrepancies)}\n\n")
        
        f.write("---\n\n")
        
        # DISCREPANCIES SECTION
        if discrepancies:
            f.write("## ⚠️ WYKRYTE ROZBIEŻNOŚCI (ALARM DOWODOWY)\n\n")
            f.write("Momenty, gdzie stan pacjenta w dokumentacji nie zgadza się z komunikacją:\n\n")
            for complaint, doc, desc in discrepancies:
                f.write(f"### 🚨 {complaint.timestamp.strftime('%Y-%m-%d')}\n\n")
                f.write(f"| Czas | Źródło | Treść |\n")
                f.write(f"|------|--------|-------|\n")
                f.write(f"| **{complaint.timestamp.strftime('%H:%M')}** | {complaint.source} ({complaint.sender}) | {complaint.content[:80]}... |\n")
                f.write(f"| **{doc.timestamp.strftime('%H:%M')}** | {doc.source} | {doc.content[:80]}... |\n\n")
                f.write(f"> {desc}\n\n")
            f.write("---\n\n")
        
        # TIMELINE BY DATE
        f.write("## 📅 CHRONOLOGIA ZDARZEŃ MEDYCZNYCH\n\n")
        
        current_date = None
        for event in medical_events:
            if event.timestamp.date() != current_date:
                current_date = event.timestamp.date()
                f.write(f"\n### 📆 {current_date.strftime('%Y-%m-%d (%A)')}\n\n")
                f.write("| Czas | Źródło | Nadawca | Treść |\n")
                f.write("|------|--------|---------|-------|\n")
            
            flag = "🚨" if event.is_discrepancy else ""
            f.write(f"| {event.timestamp.strftime('%H:%M:%S')} | {event.source} | {event.sender[:15]} | {flag} {event.content[:60]}... |\n")
    
    print(f"✅ Raport zapisany: {output_path}")

def main():
    """Główna funkcja"""
    base_path = Path(r"C:\Users\micha\.gemini\antigravity\PROJEKT POZEW")
    
    all_events: List[TimelineEvent] = []
    
    # 1. Parse Messenger (extracted_days)
    messenger_dir = base_path / "extracted_days"
    if messenger_dir.exists():
        print(f"📱 Przetwarzam Messenger ({messenger_dir})...")
        for f in messenger_dir.glob("*.txt"):
            events = parse_messenger_file(f)
            all_events.extend(events)
            if events:
                medical = sum(1 for e in events if e.is_medical)
                print(f"  - {f.name}: {len(events)} wiadomości, {medical} medycznych")
    
    # 2. Parse WhatsApp
    whatsapp_dir = base_path / "whsats up"
    if whatsapp_dir.exists():
        print(f"\n📞 Przetwarzam WhatsApp ({whatsapp_dir})...")
        for f in whatsapp_dir.glob("**/*.txt"):
            events = parse_whatsapp_file(f)
            all_events.extend(events)
            if events:
                medical = sum(1 for e in events if e.is_medical)
                print(f"  - {f.parent.name}/{f.name}: {len(events)} wiadomości, {medical} medycznych")
    
    # 3. Parse daily reports
    reports_dir = base_path / "raporty_dzien_po_dniu"
    if reports_dir.exists():
        print(f"\n📋 Przetwarzam raporty dzienne ({reports_dir})...")
        for f in reports_dir.glob("*.md"):
            events = parse_daily_report(f)
            all_events.extend(events)
    
    print(f"\n📊 PODSUMOWANIE:")
    print(f"  - Wszystkich zdarzeń: {len(all_events)}")
    print(f"  - Zdarzeń medycznych: {sum(1 for e in all_events if e.is_medical)}")
    
    # 4. Detect discrepancies
    print("\n🔍 Szukam rozbieżności...")
    discrepancies = detect_discrepancies(all_events)
    print(f"  - Znaleziono rozbieżności: {len(discrepancies)}")
    
    # 5. Generate report
    output_path = base_path / "TIMELINE_MINUTE_BY_MINUTE.md"
    generate_timeline_report(all_events, discrepancies, output_path)
    
    # 6. Save JSON for further analysis
    json_path = base_path / "timeline_data.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump([e.to_dict() for e in all_events], f, ensure_ascii=False, indent=2)
    print(f"✅ Dane JSON: {json_path}")

if __name__ == "__main__":
    main()
