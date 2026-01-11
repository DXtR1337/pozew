"""
FORENSIC SEARCH ENGINE
Główny pipeline do tworzenia MASTER_EVENT_LOG i cross-referencingu.

Kroki:
1. Indeksacja wszystkich źródeł (Messenger JSON, WhatsApp, raporty dzienne)
2. Normalizacja dat i timestampów
3. Cross-referencing z dokumentacją medyczną
4. Generowanie raportów rozbieżności
"""

import json
import re
import csv
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

# Okres III hospitalizacji
HOSP_START = datetime(2023, 4, 17)
HOSP_END = datetime(2023, 5, 30, 23, 59, 59)

# Słowa kluczowe sentymentu
NEGATIVE_KEYWORDS = [
    'boli', 'ból', 'cierpię', 'krzyczę', 'płaczę', 'mdleję', 'umrę', 'umieram',
    'głodzą', 'nie dali', 'nie przyszli', 'ignorują', 'nikt nie', 'brak',
    'okropne', 'straszne', 'najgorsze', 'na żywca', 'bez znieczulenia',
    'przez okno', 'zabijcie', 'nie wytrzymam', 'ratunku', 'pomocy',
    'tramadol', 'nie działa', 'ropa', 'gorączka', 'temperatura', 'źle'
]

POSITIVE_KEYWORDS = [
    'dobrze', 'lepiej', 'ok', 'w porządku', 'bez bólu', 'nie boli',
    'odpoczywam', 'śpię dobrze', 'poprawia się'
]

MEDICAL_ENTRIES = [
    'stan dobry', 'stan ogólny dobry', 'stabilny', 'prawidłowy', 'bez zmian',
    'pacjent w stanie dobrym', 'żywienie prawidłowe', 'odżywia się'
]

@dataclass
class Event:
    timestamp: datetime
    source: str  # MESSENGER, WHATSAPP, DOKUMENTACJA
    author: str
    content: str
    sentiment: str  # NEGATIVE, NEUTRAL, POSITIVE
    raw_file: str

def calculate_sentiment(text: str) -> str:
    """Określ sentyment wiadomości"""
    text_lower = text.lower()
    
    neg_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text_lower)
    pos_count = sum(1 for kw in POSITIVE_KEYWORDS if kw in text_lower)
    
    if neg_count >= 2:
        return "NEGATIVE"
    elif neg_count > pos_count:
        return "NEGATIVE"
    elif pos_count > neg_count:
        return "POSITIVE"
    else:
        return "NEUTRAL"

def is_medical_entry(text: str) -> bool:
    """Sprawdź czy to wpis z dokumentacji medycznej"""
    text_lower = text.lower()
    return any(entry in text_lower for entry in MEDICAL_ENTRIES)

def is_in_hospitalization(dt: datetime) -> bool:
    """Sprawdź czy data jest w okresie hospitalizacji"""
    return HOSP_START <= dt <= HOSP_END

def parse_messenger_json(base_path: Path) -> List[Event]:
    """Parsuj główny plik JSON messenger_daily_summary_all.json"""
    events = []
    json_path = base_path / "messenger_daily_summary_all.json"
    
    if not json_path.exists():
        print(f"   ⚠️ Nie znaleziono: {json_path}")
        return events
    
    with open(json_path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    
    # Struktura: {"YYYY-MM-DD": [{"sender":..., "time":..., "content":..., "ts":...}, ...]}
    for date_str, messages in data.items():
        for msg in messages:
            try:
                ts = msg.get('ts', 0)
                if ts > 0:
                    dt = datetime.fromtimestamp(ts / 1000)  # ms -> s
                else:
                    dt = datetime.strptime(f"{date_str} {msg.get('time', '00:00:00')}", "%Y-%m-%d %H:%M:%S")
                
                # Filtruj do hospitalizacji
                if not is_in_hospitalization(dt):
                    continue
                
                content = msg.get('content', '')
                if not content or content in ["[No text content]", "[Photo: 1]", "[Sticker]"]:
                    continue
                
                events.append(Event(
                    timestamp=dt,
                    source="MESSENGER",
                    author=msg.get('sender', 'Unknown'),
                    content=content[:500],
                    sentiment=calculate_sentiment(content),
                    raw_file=msg.get('source', 'unknown')
                ))
            except (ValueError, TypeError) as e:
                continue
    
    return events

def parse_whatsapp_files(base_path: Path) -> List[Event]:
    """Parsuj pliki WhatsApp"""
    events = []
    whatsapp_dir = base_path / "whsats up"
    
    if not whatsapp_dir.exists():
        return events
    
    for f in whatsapp_dir.glob("**/*.txt"):
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        pattern = r'(\d{1,2}\.\d{1,2}\.\d{4}),\s*(\d{1,2}:\d{2})\s*-\s*([^:]+):\s*(.+)'
        matches = re.findall(pattern, content)
        
        for date_str, time_str, sender, text in matches:
            try:
                dt = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")
                
                if not is_in_hospitalization(dt):
                    continue
                
                if 'Pominięto multimedia' in text or 'załączony plik' in text:
                    continue
                
                events.append(Event(
                    timestamp=dt,
                    source="WHATSAPP",
                    author=sender.strip(),
                    content=text.strip()[:500],
                    sentiment=calculate_sentiment(text),
                    raw_file=str(f)
                ))
            except ValueError:
                continue
    
    return events

def parse_daily_reports(base_path: Path) -> List[Event]:
    """Parsuj raporty dzienne (traktowane jako dokumentacja)"""
    events = []
    reports_dir = base_path / "raporty_dzien_po_dniu"
    
    if not reports_dir.exists():
        return events
    
    for f in reports_dir.glob("*.md"):
        # Wyciągnij datę z nazwy pliku (format: YYYY-MM-DD.md)
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', f.name)
        if not date_match:
            continue
        
        date_str = date_match.group(1)
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue
        
        if not is_in_hospitalization(dt):
            continue
        
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Wyciągnij kluczowe cytaty z dokumentacji
        if is_medical_entry(content):
            events.append(Event(
                timestamp=dt.replace(hour=12),  # Środek dnia jako domyślna godzina
                source="DOKUMENTACJA",
                author="Szpital",
                content=f"[Raport dzienny z {date_str}]",
                sentiment="NEUTRAL",
                raw_file=str(f)
            ))
    
    return events

def generate_master_event_log(events: List[Event], output_path: Path):
    """Generuj MASTER_EVENT_LOG.csv"""
    
    events.sort(key=lambda x: x.timestamp)
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['TIMESTAMP', 'DATE', 'TIME', 'SOURCE', 'AUTHOR', 'SENTIMENT', 'CONTENT', 'RAW_FILE'])
        
        for e in events:
            writer.writerow([
                e.timestamp.isoformat(),
                e.timestamp.strftime('%Y-%m-%d'),
                e.timestamp.strftime('%H:%M:%S'),
                e.source,
                e.author[:50],
                e.sentiment,
                e.content[:200],
                e.raw_file[-80:] if len(e.raw_file) > 80 else e.raw_file
            ])
    
    print(f"✅ MASTER_EVENT_LOG.csv zapisany: {output_path}")
    print(f"   Rekordów: {len(events)}")

def detect_discrepancies(events: List[Event]) -> List[Dict]:
    """Wykryj rozbieżności: dokumentacja mówi 'dobry' ale pacjent cierpi"""
    discrepancies = []
    
    # Grupuj po dniach
    by_date = defaultdict(list)
    for e in events:
        by_date[e.timestamp.date()].append(e)
    
    for date, day_events in by_date.items():
        # Znajdź negatywne wiadomości pacjenta
        patient_negative = [e for e in day_events 
                          if e.sentiment == "NEGATIVE" 
                          and ("Michał" in e.author or "Wiencek" in e.author or "Es" in e.author)]
        
        # Znajdź pozytywne wpisy z dokumentacji
        doc_positive = [e for e in day_events
                       if e.source == "DOKUMENTACJA" and is_medical_entry(e.content)]
        
        if patient_negative and doc_positive:
            for pn in patient_negative[:3]:  # Max 3 przykłady na dzień
                for dp in doc_positive:
                    time_diff = abs((dp.timestamp - pn.timestamp).total_seconds() / 3600)
                    if time_diff <= 4:  # W ciągu 4 godzin
                        discrepancies.append({
                            'date': date,
                            'patient_msg': pn,
                            'doc_entry': dp,
                            'time_diff_hours': time_diff
                        })
    
    return discrepancies

def generate_discrepancy_report(discrepancies: List[Dict], output_path: Path):
    """Generuj raport rozbieżności"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 🔍 RAPORT ROZBIEŻNOŚCI: Dokumentacja vs Rzeczywistość\n\n")
        f.write("**Cel:** Wykrycie momentów, gdzie dokumentacja szpitalna mówi 'stan dobry', ale pacjent jednocześnie cierpi.\n\n")
        f.write(f"**Znaleziono rozbieżności:** {len(discrepancies)}\n\n")
        
        if not discrepancies:
            f.write("## ✅ Brak wykrytych rozbieżności\n\n")
            f.write("Nie znaleziono momentów, gdzie dokumentacja i stan pacjenta są sprzeczne.\n")
            f.write("**UWAGA:** To może oznaczać, że raporty dzienne nie zawierają fraz typu 'stan dobry'.\n")
            print(f"✅ Raport rozbieżności zapisany (brak wyników): {output_path}")
            return
        
        f.write("> [!CAUTION]\n")
        f.write("> Każda rozbieżność to potencjalny dowód fałszowania dokumentacji medycznej.\n\n")
        f.write("---\n\n")
        
        for i, d in enumerate(discrepancies[:20], 1):
            f.write(f"### 🚨 Rozbieżność #{i}: {d['date']}\n\n")
            
            f.write("| Aspekt | Dokumentacja | Pacjent (reality) |\n")
            f.write("|--------|--------------|-------------------|\n")
            f.write(f"| Czas | {d['doc_entry'].timestamp.strftime('%H:%M')} | {d['patient_msg'].timestamp.strftime('%H:%M')} |\n")
            f.write(f"| Treść | {d['doc_entry'].content[:60]}... | {d['patient_msg'].content[:60]}... |\n")
            f.write(f"| Sentyment | NEUTRAL/POSITIVE | **{d['patient_msg'].sentiment}** |\n\n")
            
            f.write(f"> **Pełny cytat pacjenta:** \"{d['patient_msg'].content[:150]}...\"\n\n")
            f.write(f"> **Różnica czasowa:** {d['time_diff_hours']:.1f} godzin\n\n")
            f.write("---\n\n")
    
    print(f"✅ Raport rozbieżności zapisany: {output_path}")

def generate_forensic_summary(events: List[Event], output_path: Path):
    """Generuj podsumowanie forensic"""
    
    # Statystyki
    by_source = defaultdict(int)
    by_sentiment = defaultdict(int)
    by_date = defaultdict(int)
    
    for e in events:
        by_source[e.source] += 1
        by_sentiment[e.sentiment] += 1
        by_date[e.timestamp.date()] += 1
    
    # Znajdź wiadomości z kluczowymi frazami
    keyword_hits = defaultdict(list)
    search_phrases = ['na żywca', 'bez znieczulenia', 'głodzą', 'ignorują', 'krzyczałem', 'boli']
    
    for e in events:
        for phrase in search_phrases:
            if phrase.lower() in e.content.lower():
                keyword_hits[phrase].append(e)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 📊 FORENSIC SUMMARY: Analiza Danych\n\n")
        f.write(f"**Okres:** III hospitalizacja (17.04.2023 - 30.05.2023)\n")
        f.write(f"**Wszystkich zdarzeń:** {len(events)}\n\n")
        
        f.write("## Rozkład po źródłach\n\n")
        f.write("| Źródło | Liczba |\n")
        f.write("|--------|--------|\n")
        for src, count in sorted(by_source.items(), key=lambda x: -x[1]):
            f.write(f"| {src} | {count} |\n")
        
        f.write("\n## Rozkład sentymentu\n\n")
        f.write("| Sentyment | Liczba | % |\n")
        f.write("|-----------|--------|---|\n")
        total = len(events)
        for sent, count in sorted(by_sentiment.items(), key=lambda x: -x[1]):
            pct = (count / total * 100) if total > 0 else 0
            emoji = "🔴" if sent == "NEGATIVE" else "🟢" if sent == "POSITIVE" else "🟡"
            f.write(f"| {emoji} {sent} | {count} | {pct:.1f}% |\n")
        
        f.write("\n## 🎯 Trafienia kluczowych fraz\n\n")
        for phrase in sorted(keyword_hits.keys(), key=lambda x: -len(keyword_hits[x])):
            hits = keyword_hits[phrase]
            f.write(f"### \"{phrase}\" ({len(hits)} trafień)\n\n")
            for h in hits[:3]:
                f.write(f"- **{h.timestamp.strftime('%Y-%m-%d %H:%M')}** ({h.author[:20]}): \"{h.content[:80]}...\"\n")
            f.write("\n")
    
    print(f"✅ Forensic Summary zapisany: {output_path}")

def main():
    base_path = Path(r"C:\Users\micha\.gemini\antigravity\PROJEKT POZEW")
    
    print("🔬 FORENSIC SEARCH ENGINE")
    print(f"   Okres: {HOSP_START.date()} - {HOSP_END.date()}")
    print("=" * 60)
    
    all_events: List[Event] = []
    
    # 1. Messenger JSON
    print("\n📱 Parsowanie messenger_daily_summary_all.json...")
    messenger_events = parse_messenger_json(base_path)
    all_events.extend(messenger_events)
    print(f"   Znaleziono: {len(messenger_events)} wiadomości w okresie hospitalizacji")
    
    neg = sum(1 for e in messenger_events if e.sentiment == "NEGATIVE")
    print(f"   Negatywnych: {neg}")
    
    # 2. WhatsApp
    print("\n📞 Parsowanie WhatsApp...")
    whatsapp_events = parse_whatsapp_files(base_path)
    all_events.extend(whatsapp_events)
    print(f"   Znaleziono: {len(whatsapp_events)} wiadomości")
    
    # 3. Raporty dzienne (jako dokumentacja)
    print("\n📋 Parsowanie raportów dziennych...")
    doc_events = parse_daily_reports(base_path)
    all_events.extend(doc_events)
    print(f"   Znaleziono: {len(doc_events)} wpisów dokumentacji")
    
    print(f"\n📊 ŁĄCZNIE: {len(all_events)} zdarzeń")
    
    # Generuj MASTER_EVENT_LOG
    print("\n💾 Generowanie MASTER_EVENT_LOG.csv...")
    master_log_path = base_path / "MASTER_EVENT_LOG.csv"
    generate_master_event_log(all_events, master_log_path)
    
    # Wykryj rozbieżności
    print("\n🔍 Szukam rozbieżności dokumentacja vs rzeczywistość...")
    discrepancies = detect_discrepancies(all_events)
    print(f"   Znaleziono: {len(discrepancies)} potencjalnych rozbieżności")
    
    # Generuj raport rozbieżności
    discrepancy_path = base_path / "RAPORT_ROZBIEZNOSCI_DOK_VS_RZECZYWISTOSC.md"
    generate_discrepancy_report(discrepancies, discrepancy_path)
    
    # Generuj summary
    summary_path = base_path / "FORENSIC_SUMMARY.md"
    generate_forensic_summary(all_events, summary_path)
    
    print("\n" + "=" * 60)
    print("✅ FORENSIC SEARCH ZAKOŃCZONY")
    print(f"   Pliki wyjściowe:")
    print(f"   - {master_log_path}")
    print(f"   - {discrepancy_path}")
    print(f"   - {summary_path}")

if __name__ == "__main__":
    main()
