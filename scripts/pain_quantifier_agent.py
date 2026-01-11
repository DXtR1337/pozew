"""
FORENSIC DEEP DIVE - Pain Quantifier Agent V2 (FIXED)
Audytor Bólu: Kwantyfikacja bólu TYLKO w okresie hospitalizacji, z kontekstem medycznym.

Okres III hospitalizacji: 17.04.2023 - 30.05.2023
"""

import re
from datetime import datetime, date
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Tuple
import csv

# DATY HOSPITALIZACJI (III hospitalizacja - chirurgia Bielsko)
HOSP_START = date(2023, 4, 17)
HOSP_END = date(2023, 5, 30)

# Frazy bólowe MEDYCZNE (nie pojedyncze słowa, ale kontekstowe frazy)
PAIN_PHRASES = {
    # Poziom 10 - Krytyczny (ból + kontekst medyczny/suicydalny)
    'na żywca': 10,
    'bez znieczulenia': 10,
    'nigdy nie płakałem tyle': 10,
    'chcę umrzeć': 10,
    'skoczyć przez okno': 10,
    'przez okno': 9,  # tylko w kontekście suicydalnym
    'zabijcie mnie': 10,
    
    # Poziom 9 - Ekstremalny (ból podczas zabiegów)
    'rurkę wbijali': 9,
    'wbijanie': 9,
    'wpierdalanie rurki': 9,
    'w chuj boli': 9,
    'w chuj mnie to bolało': 9,
    'ból nie do zniesienia': 9,
    'krzyczałem': 9,
    'płakałem': 8,
    'wycie': 8,
    
    # Poziom 8 - Bardzo silny (ból przy opatrunkach, drenażu)
    'opatrunek boli': 8,
    'zmiana opatrunku': 7,
    'ruszają rurką': 8,
    'dren boli': 8,
    'wsadzają siatkę': 8,
    'ropa leci': 7,
    'ropa się leje': 7,
    
    # Poziom 7 - Silny (tramadol nie działa)
    'tramadol nie pomaga': 7,
    'tramadol chuja pomaga': 8,
    'lek nie działa': 7,
    'nawet przy tramadolu': 7,
    'nie mogę spać od bólu': 7,
    'nie śpię': 6,
    'całą noc': 6,
    
    # Poziom 6 - Znaczący (ból brzucha związany z ropniem)
    'brzuch boli': 6,
    'boli mnie brzuch': 6,
    'ból brzucha': 6,
    'ropień boli': 7,
    'rana boli': 6,
    
    # Poziom 5 - Umiarkowany (ogólny ból szpitalny)
    'boli mnie': 5,
    'cierpię': 5,
    'źle się czuję': 4,
}

# Kontekst MEDYCZNY - wiadomość musi zawierać przynajmniej jedno z tych słów
MEDICAL_CONTEXT = [
    'szpital', 'lekarz', 'pielęgniarka', 'zabieg', 'operacja', 'drenaż', 'dren',
    'ropień', 'rana', 'opatrunek', 'antybiotyk', 'tramadol', 'zastrzyk', 'kroplówka',
    'ból', 'boli', 'chirurg', 'oddział', 'izolatka', 'sala', 'łóżko', 'brzuch',
    'TK', 'badanie', 'posiew', 'bakteria', 'gorączka', 'temperatura', 'mdleję',
    'na żywca', 'bez znieczulenia', 'ropa', 'sączek', 'nutridrinki', 'głodzą',
    'psycholog', 'samobójcz', 'okno', 'skoczyć'
]

@dataclass
class PainEvent:
    timestamp: datetime
    source: str
    content: str
    pain_score: int
    matched_phrase: str
    full_context: str  # Pełna wiadomość dla kontekstu

def has_medical_context(text: str) -> bool:
    """Sprawdź czy wiadomość ma kontekst medyczny"""
    text_lower = text.lower()
    return any(ctx in text_lower for ctx in MEDICAL_CONTEXT)

def calculate_pain_score(text: str) -> Tuple[int, str]:
    """Oblicz wynik bólu - znajdź NAJLEPSZĄ pasującą frazę"""
    text_lower = text.lower()
    best_score = 0
    best_phrase = ""
    
    for phrase, score in PAIN_PHRASES.items():
        if phrase.lower() in text_lower:
            if score > best_score:
                best_score = score
                best_phrase = phrase
    
    return best_score, best_phrase

def is_in_hospitalization(dt: datetime) -> bool:
    """Sprawdź czy data jest w okresie hospitalizacji"""
    return HOSP_START <= dt.date() <= HOSP_END

def parse_all_messages(base_path: Path) -> List[PainEvent]:
    """Parsuj wiadomości TYLKO z okresu hospitalizacji i z kontekstem medycznym"""
    events = []
    
    # Messenger
    messenger_dir = base_path / "extracted_days"
    if messenger_dir.exists():
        for f in messenger_dir.glob("*.txt"):
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', f.name)
            if not date_match:
                continue
            
            date_str = date_match.group(1)
            file_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            # FILTR: Tylko daty z hospitalizacji
            if not (HOSP_START <= file_date <= HOSP_END):
                continue
            
            with open(f, 'r', encoding='utf-8') as file:
                content = file.read()
            
            pattern = r'\|\s*(\d{2}:\d{2}:\d{2})\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|'
            matches = re.findall(pattern, content)
            
            for time_str, sender, text in matches:
                try:
                    timestamp = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
                    text = text.strip()
                    sender = sender.strip()
                    
                    if text in ["[No text content]", "[Photo: 1]", "[Sticker]"]:
                        continue
                    
                    # Tylko wiadomości pacjenta
                    if "Michał" not in sender and "Wiencek" not in sender:
                        continue
                    
                    # FILTR: Musi mieć kontekst medyczny
                    if not has_medical_context(text):
                        continue
                    
                    pain, phrase = calculate_pain_score(text)
                    if pain > 0:
                        events.append(PainEvent(
                            timestamp=timestamp,
                            source="MESSENGER",
                            content=text[:300],
                            pain_score=pain,
                            matched_phrase=phrase,
                            full_context=text
                        ))
                except ValueError:
                    continue
    
    # WhatsApp
    whatsapp_dir = base_path / "whsats up"
    if whatsapp_dir.exists():
        for f in whatsapp_dir.glob("**/*.txt"):
            with open(f, 'r', encoding='utf-8') as file:
                content = file.read()
            
            pattern = r'(\d{1,2}\.\d{1,2}\.\d{4}),\s*(\d{1,2}:\d{2})\s*-\s*([^:]+):\s*(.+)'
            matches = re.findall(pattern, content)
            
            for date_str, time_str, sender, text in matches:
                try:
                    timestamp = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")
                    
                    # FILTR: Tylko daty z hospitalizacji
                    if not is_in_hospitalization(timestamp):
                        continue
                    
                    # Tylko wiadomości pacjenta (Es/Michał)
                    if "Es" not in sender and "Michał" not in sender:
                        continue
                    
                    # FILTR: Musi mieć kontekst medyczny
                    if not has_medical_context(text):
                        continue
                    
                    pain, phrase = calculate_pain_score(text)
                    if pain > 0:
                        events.append(PainEvent(
                            timestamp=timestamp,
                            source="WHATSAPP",
                            content=text[:300],
                            pain_score=pain,
                            matched_phrase=phrase,
                            full_context=text
                        ))
                except ValueError:
                    continue
    
    events.sort(key=lambda x: x.timestamp)
    return events

def generate_pain_report(events: List[PainEvent], output_path: Path):
    """Generuj poprawiony raport bólu"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 🔥 RAPORT AUDYTORA BÓLU V2: Kwantyfikacja Cierpienia\n\n")
        f.write("**Okres:** III hospitalizacja (17.04.2023 - 30.05.2023)\n")
        f.write("**Metodologia:** Tylko wiadomości z kontekstem medycznym, frazy zamiast pojedynczych słów\n\n")
        
        if not events:
            f.write("## ⚠️ Brak wyników\n\nNie znaleziono wiadomości spełniających kryteria.\n")
            print(f"✅ Raport zapisany (brak wyników): {output_path}")
            return
        
        # Statystyki
        high_pain = [e for e in events if e.pain_score >= 7]
        critical_pain = [e for e in events if e.pain_score >= 9]
        
        f.write("## 📊 Statystyki\n\n")
        f.write(f"| Metryka | Wartość |\n")
        f.write(f"|---------|--------|\n")
        f.write(f"| Wiadomości z bólem (kontekst medyczny) | {len(events)} |\n")
        f.write(f"| Wiadomości z bólem ≥7/10 | **{len(high_pain)}** |\n")
        f.write(f"| Wiadomości z bólem krytycznym (≥9/10) | **{len(critical_pain)}** 🔴 |\n")
        f.write(f"| Średni poziom bólu | {sum(e.pain_score for e in events)/len(events):.1f}/10 |\n\n")
        
        f.write("---\n\n")
        
        # TOP najgorsze momenty - pełne cytaty
        f.write("## 🚨 NAJGORSZE MOMENTY (pełne cytaty)\n\n")
        
        worst = sorted(events, key=lambda x: x.pain_score, reverse=True)
        
        for i, e in enumerate(worst[:15], 1):
            emoji = "🔴" if e.pain_score >= 9 else "🟠" if e.pain_score >= 7 else "🟡"
            f.write(f"### {emoji} #{i}: {e.timestamp.strftime('%Y-%m-%d %H:%M')} (Ból: {e.pain_score}/10)\n\n")
            f.write(f"**Dopasowana fraza:** `{e.matched_phrase}`\n\n")
            f.write(f"> {e.content}\n\n")
            f.write(f"*Źródło: {e.source}*\n\n")
            f.write("---\n\n")
        
        # Rozkład po dniach (tylko hospitalizacja)
        f.write("## 📅 Rozkład po dniach hospitalizacji\n\n")
        
        by_date = defaultdict(list)
        for e in events:
            by_date[e.timestamp.date()].append(e)
        
        f.write("| Data | Wiadomości | Max ból | Najgorsza fraza |\n")
        f.write("|------|------------|---------|----------------|\n")
        for dt in sorted(by_date.keys()):
            day_events = by_date[dt]
            max_e = max(day_events, key=lambda x: x.pain_score)
            flag = "🔴" if max_e.pain_score >= 9 else "🟠" if max_e.pain_score >= 7 else ""
            f.write(f"| {dt} | {len(day_events)} | {max_e.pain_score}/10 {flag} | {max_e.matched_phrase} |\n")
    
    print(f"✅ Raport bólu V2 zapisany: {output_path}")

def main():
    base_path = Path(r"C:\Users\micha\.gemini\antigravity\PROJEKT POZEW")
    
    print("🔥 AGENT AUDYTOR BÓLU V2 (FIXED)")
    print(f"   Okres: {HOSP_START} - {HOSP_END}")
    print("=" * 50)
    
    print("📱 Parsowanie wiadomości (tylko hospitalizacja + kontekst medyczny)...")
    events = parse_all_messages(base_path)
    print(f"   Znaleziono: {len(events)} wiadomości spełniających kryteria")
    
    # Generuj raport
    report_path = base_path / "RAPORT_AUDYTORA_BOLU_KWANTYFIKACJA.md"
    generate_pain_report(events, report_path)
    
    print("\n" + "=" * 50)
    print("✅ ZAKOŃCZONO")

if __name__ == "__main__":
    main()
