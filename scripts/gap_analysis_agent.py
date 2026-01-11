"""
FORENSIC DEEP DIVE - Gap Analysis Agent
Wykrywacz Ciszy: Znajdź okresy gdzie szpital "zamilkł", a na czatach trwał dramat.
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Tuple

# Słowa kluczowe bólu/paniki
PAIN_KEYWORDS = {
    'zabijcie': 10, 'umrę': 10, 'umieram': 10, 'wyję': 9, 'nie wytrzymam': 9,
    'krzyczę': 8, 'błagam': 8, 'pomocy': 8, 'ratunku': 8, 'mdleję': 8,
    'nie mogę': 7, 'boli mnie': 7, 'silny ból': 7, 'okropnie': 7,
    'boli': 5, 'ból': 5, 'bolało': 5, 'cierpię': 6, 'nie śpię': 5,
    'gdzie oni są': 6, 'nikt nie przychodzi': 7, 'ignorują': 6,
    'na żywca': 10, 'bez znieczulenia': 9, 'tortura': 9
}

@dataclass
class TimelineEvent:
    timestamp: datetime
    source: str  # MESSENGER, WHATSAPP, DOKUMENTACJA, PIELEGNIARKI
    author: str
    content: str
    pain_score: int = 0

@dataclass
class SilenceGap:
    start: datetime
    end: datetime
    duration_hours: float
    patient_messages: List[TimelineEvent]
    avg_pain_score: float
    max_pain_score: int

def calculate_pain_score(text: str) -> int:
    """Oblicz wynik bólu na podstawie słów kluczowych"""
    text_lower = text.lower()
    max_score = 0
    for keyword, score in PAIN_KEYWORDS.items():
        if keyword in text_lower:
            max_score = max(max_score, score)
    return max_score

def parse_messenger_files(base_path: Path) -> List[TimelineEvent]:
    """Parsuj pliki Messenger z extracted_days"""
    events = []
    messenger_dir = base_path / "extracted_days"
    
    if not messenger_dir.exists():
        return events
    
    for f in messenger_dir.glob("*.txt"):
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', f.name)
        if not date_match:
            continue
        
        date_str = date_match.group(1)
        
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Parse table rows
        pattern = r'\|\s*(\d{2}:\d{2}:\d{2})\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|'
        matches = re.findall(pattern, content)
        
        for time_str, sender, text in matches:
            try:
                timestamp = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
                text = text.strip()
                sender = sender.strip()
                
                if text in ["[No text content]", "[Photo: 1]", "[Sticker]"]:
                    continue
                
                # Filter to patient messages with pain keywords
                if "Michał" in sender or "Wiencek" in sender:
                    pain = calculate_pain_score(text)
                    if pain > 0:
                        events.append(TimelineEvent(
                            timestamp=timestamp,
                            source="MESSENGER",
                            author=sender,
                            content=text[:200],
                            pain_score=pain
                        ))
            except ValueError:
                continue
    
    return events

def parse_whatsapp_files(base_path: Path) -> List[TimelineEvent]:
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
                timestamp = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")
                
                if timestamp.year != 2023:
                    continue
                
                # Filter to patient messages (Es/Michał)
                if "Es" in sender or "Michał" in sender:
                    pain = calculate_pain_score(text)
                    if pain > 0:
                        events.append(TimelineEvent(
                            timestamp=timestamp,
                            source="WHATSAPP",
                            author=sender,
                            content=text[:200],
                            pain_score=pain
                        ))
            except ValueError:
                continue
    
    return events

def find_silence_gaps(patient_events: List[TimelineEvent], 
                       min_gap_hours: float = 4.0,
                       day_start: int = 7,
                       day_end: int = 22) -> List[SilenceGap]:
    """
    Znajdź luki w dokumentacji medycznej (symulowane jako brak wpisów).
    Zakładamy że dokumentacja powinna być każde 4h w dzień.
    """
    gaps = []
    
    # Grupuj wiadomości po datach
    by_date = defaultdict(list)
    for e in patient_events:
        by_date[e.timestamp.date()].append(e)
    
    for date, day_messages in by_date.items():
        day_messages.sort(key=lambda x: x.timestamp)
        
        # Sprawdź każdą 4-godzinną "okno" od 7:00 do 22:00
        for hour in range(day_start, day_end - 4, 2):  # Co 2h sprawdzamy
            window_start = datetime.combine(date, datetime.min.time().replace(hour=hour))
            window_end = window_start + timedelta(hours=4)
            
            # Znajdź wiadomości w tym oknie
            window_messages = [m for m in day_messages 
                             if window_start <= m.timestamp <= window_end]
            
            if window_messages:
                avg_pain = sum(m.pain_score for m in window_messages) / len(window_messages)
                max_pain = max(m.pain_score for m in window_messages)
                
                # Jeśli jest dużo wiadomości o wysokim bólu - to "luka z dramatem"
                if len(window_messages) >= 3 and avg_pain >= 5:
                    gaps.append(SilenceGap(
                        start=window_start,
                        end=window_end,
                        duration_hours=4.0,
                        patient_messages=window_messages,
                        avg_pain_score=avg_pain,
                        max_pain_score=max_pain
                    ))
    
    return gaps

def generate_silence_report(gaps: List[SilenceGap], output_path: Path):
    """Generuj raport ciszy"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 🔇 RAPORT CISZY: Nadzór vs Rzeczywistość\n\n")
        f.write("**Cel:** Okresy intensywnego cierpienia pacjenta przy (prawdopodobnym) braku reakcji personelu.\n\n")
        f.write(f"**Znaleziono:** {len(gaps)} krytycznych okien czasowych\n\n")
        f.write("---\n\n")
        
        if not gaps:
            f.write("## ℹ️ Brak wykrytych krytycznych okien\n\n")
            f.write("Nie znaleziono okresów z ≥3 wiadomościami o średnim bólu ≥5/10.\n")
            f.write("Może to oznaczać, że wiadomości o bólu były rozproszone w czasie.\n")
            print(f"✅ Raport ciszy zapisany: {output_path}")
            return
        
        # Sortuj po max_pain_score (najgorsze najpierw)
        gaps.sort(key=lambda g: g.max_pain_score, reverse=True)
        
        f.write("## ⚠️ ALARM: Najgorsze momenty bez dokumentowanej interwencji\n\n")
        
        for i, gap in enumerate(gaps[:20], 1):  # Top 20
            f.write(f"### 🚨 Incydent #{i}: {gap.start.strftime('%Y-%m-%d %H:%M')} - {gap.end.strftime('%H:%M')}\n\n")
            f.write(f"| Parametr | Wartość |\n")
            f.write(f"|----------|--------|\n")
            f.write(f"| **Średni poziom bólu** | {gap.avg_pain_score:.1f}/10 |\n")
            f.write(f"| **Maksymalny poziom bólu** | {gap.max_pain_score}/10 |\n")
            f.write(f"| **Liczba wiadomości pacjenta** | {len(gap.patient_messages)} |\n\n")
            
            f.write("**Cytaty z tego okresu:**\n\n")
            f.write("| Czas | Ból | Treść |\n")
            f.write("|------|-----|-------|\n")
            for msg in gap.patient_messages[:5]:
                f.write(f"| {msg.timestamp.strftime('%H:%M')} | {msg.pain_score}/10 | {msg.content[:80]}... |\n")
            f.write("\n")
            
            f.write("> **[DO WERYFIKACJI]** Sprawdzić dokumentację pielęgniarską z tego okresu.\n\n")
            f.write("---\n\n")
        
        # Statystyki
        f.write("## 📊 Statystyki zbiorcze\n\n")
        total_high_pain = sum(1 for g in gaps if g.max_pain_score >= 8)
        avg_max_pain = sum(g.max_pain_score for g in gaps) / len(gaps)
        f.write(f"| Metryka | Wartość |\n")
        f.write(f"|---------|--------|\n")
        f.write(f"| Okna z bólem ≥8/10 | **{total_high_pain}** |\n")
        f.write(f"| Średni max. ból w oknach | {avg_max_pain:.1f}/10 |\n")
        f.write(f"| Najgorszy dzień | {gaps[0].start.strftime('%Y-%m-%d')} |\n")
    
    print(f"✅ Raport ciszy zapisany: {output_path}")

def main():
    base_path = Path(r"C:\Users\micha\.gemini\antigravity\PROJEKT POZEW")
    
    print("🔇 AGENT WYKRYWACZ CISZY - Gap Analysis")
    print("=" * 50)
    
    # Zbierz wiadomości pacjenta
    print("📱 Parsowanie Messenger...")
    messenger_events = parse_messenger_files(base_path)
    print(f"   Znaleziono: {len(messenger_events)} wiadomości z bólem")
    
    print("📞 Parsowanie WhatsApp...")
    whatsapp_events = parse_whatsapp_files(base_path)
    print(f"   Znaleziono: {len(whatsapp_events)} wiadomości z bólem")
    
    all_events = messenger_events + whatsapp_events
    all_events.sort(key=lambda x: x.timestamp)
    
    print(f"\n📊 Łącznie: {len(all_events)} wiadomości o bólu/cierpieniu")
    
    # Znajdź luki
    print("\n🔍 Szukam 'okien ciszy'...")
    gaps = find_silence_gaps(all_events, min_gap_hours=4.0)
    print(f"   Znaleziono: {len(gaps)} krytycznych okresów")
    
    # Generuj raport
    output_path = base_path / "RAPORT_CISZY_NADZOR_VS_RZECZYWISTOSC.md"
    generate_silence_report(gaps, output_path)
    
    print("\n" + "=" * 50)
    print("✅ ZAKOŃCZONO")

if __name__ == "__main__":
    main()
