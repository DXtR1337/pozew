"""
FORENSIC DEEP DIVE - NFZ Fraud Hunter Agent
Weryfikator Finansowy: Znajdź procedury wpisane w wypis, których nie wykonano.
"""

import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple
from datetime import datetime
from collections import defaultdict

# Procedury typowo rozliczane z NFZ
NFZ_PROCEDURES = {
    'żywienie pozajelitowe': ['TPN', 'żywienie pozajelitowe', 'żywienie parenteralne', 'worek żywieniowy'],
    'konsultacja psychologiczna': ['psycholog', 'konsultacja psychologiczna', 'wsparcie psychologiczne'],
    'konsultacja psychiatryczna': ['psychiatra', 'konsultacja psychiatryczna'],
    'fizjoterapia': ['fizjoterapia', 'rehabilitacja', 'pionizacja'],
    'toaleta rany': ['toaleta rany', 'opatrunek', 'zmiana opatrunku'],
    'konsultacja gastroenterologiczna': ['gastroenterolog', 'konsultacja gastro'],
    'konsultacja stomatologiczna': ['stomatolog', 'dentysta', 'konsultacja stomatologiczna'],
    'antybiotykoterapia celowana': ['antybiotyk celowany', 'leczenie celowane', 'antybiogram'],
    'posiew mikrobiologiczny': ['posiew', 'badanie mikrobiologiczne'],
    'badanie obrazowe (TK/MRI)': ['TK', 'tomografia', 'MRI', 'rezonans'],
}

# Frazy sugerujące że procedura się NIE odbyła
DENIAL_PHRASES = {
    'żywienie pozajelitowe': [
        'nie dostałem jedzenia', 'głodzą mnie', 'nic nie jem', 'tylko nutridrinki',
        'nie dali mi jeść', 'głodny', 'TPN nie było', 'nie było żywienia'
    ],
    'konsultacja psychologiczna': [
        'psycholog nie przyszedł', 'nie było psychologa', 'nikt nie przyszedł',
        'obiecali psychologa', 'miał przyjść psycholog', 'czekam na psychologa'
    ],
    'toaleta rany': [
        'brudny opatrunek', 'nie zmienili opatrunku', 'czekałem na opatrunek',
        'nie przyszli zmieniać', 'opatrunek przez godziny'
    ],
    'konsultacja stomatologiczna': [
        'nie dali stomatologa', 'ból zęba', 'odmówili stomatologa',
        'tylko przeciwbólowy', 'ząb boli'
    ],
    'posiew mikrobiologiczny': [
        'nie wzięli posiewu', 'nie zrobili posiewu', 'posiewu nie zrobili',
        'nie wiem czy wzięli posiew'
    ],
}

@dataclass
class ProcedureClaim:
    procedure_name: str
    source: str  # WYPIS lub DOKUMENTACJA
    date: str
    
@dataclass
class DenialEvidence:
    procedure_name: str
    denial_phrase: str
    source: str  # MESSENGER, WHATSAPP
    timestamp: datetime
    full_quote: str

def scan_for_denial_phrases(base_path: Path) -> List[DenialEvidence]:
    """Przeszukaj czaty w poszukiwaniu fraz zaprzeczających procedurom"""
    evidence = []
    
    # Messenger
    messenger_dir = base_path / "extracted_days"
    if messenger_dir.exists():
        for f in messenger_dir.glob("*.txt"):
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', f.name)
            if not date_match:
                continue
            
            date_str = date_match.group(1)
            
            with open(f, 'r', encoding='utf-8') as file:
                content = file.read()
            
            pattern = r'\|\s*(\d{2}:\d{2}:\d{2})\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|'
            matches = re.findall(pattern, content)
            
            for time_str, sender, text in matches:
                text_lower = text.lower()
                
                # Sprawdź każdą procedurę
                for proc_name, denial_list in DENIAL_PHRASES.items():
                    for denial in denial_list:
                        if denial.lower() in text_lower:
                            try:
                                timestamp = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
                                evidence.append(DenialEvidence(
                                    procedure_name=proc_name,
                                    denial_phrase=denial,
                                    source="MESSENGER",
                                    timestamp=timestamp,
                                    full_quote=text.strip()[:200]
                                ))
                            except ValueError:
                                pass
    
    # WhatsApp
    whatsapp_dir = base_path / "whsats up"
    if whatsapp_dir.exists():
        for f in whatsapp_dir.glob("**/*.txt"):
            with open(f, 'r', encoding='utf-8') as file:
                content = file.read()
            
            pattern = r'(\d{1,2}\.\d{1,2}\.\d{4}),\s*(\d{1,2}:\d{2})\s*-\s*([^:]+):\s*(.+)'
            matches = re.findall(pattern, content)
            
            for date_str, time_str, sender, text in matches:
                text_lower = text.lower()
                
                for proc_name, denial_list in DENIAL_PHRASES.items():
                    for denial in denial_list:
                        if denial.lower() in text_lower:
                            try:
                                timestamp = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")
                                if timestamp.year == 2023:
                                    evidence.append(DenialEvidence(
                                        procedure_name=proc_name,
                                        denial_phrase=denial,
                                        source="WHATSAPP",
                                        timestamp=timestamp,
                                        full_quote=text.strip()[:200]
                                    ))
                            except ValueError:
                                pass
    
    return evidence

def generate_fraud_report(evidence: List[DenialEvidence], output_path: Path):
    """Generuj raport potencjalnych wyłudzeń"""
    
    # Grupuj po procedurze
    by_procedure = defaultdict(list)
    for e in evidence:
        by_procedure[e.procedure_name].append(e)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 💰 RAPORT WERYFIKATORA NFZ: Usługi Widmo\n\n")
        f.write("**Cel:** Identyfikacja procedur zafakturowanych, a niewykonanych (Art. 286 KK - oszustwo)\n\n")
        f.write(f"**Przeanalizowano:** Messenger + WhatsApp (04-05.2023)\n")
        f.write(f"**Znaleziono dowodów negacji:** {len(evidence)}\n\n")
        
        f.write("> [!CAUTION]\n")
        f.write("> Ten raport wymaga weryfikacji z Kartą Wypisową szpitala.\n")
        f.write("> Jeśli procedura jest wpisana w wypis, a pacjent twierdzi że jej nie było - to POTENCJALNE WYŁUDZENIE.\n\n")
        f.write("---\n\n")
        
        # Podsumowanie
        f.write("## 📊 Podsumowanie potencjalnych \"Usług Widmo\"\n\n")
        f.write("| Procedura | Liczba zaprzeczeń | Status |\n")
        f.write("|-----------|-------------------|--------|\n")
        for proc_name in sorted(by_procedure.keys(), key=lambda x: len(by_procedure[x]), reverse=True):
            count = len(by_procedure[proc_name])
            status = "🔴 SPRAWDŹ PILNIE" if count >= 3 else "🟡 Zweryfikuj"
            f.write(f"| {proc_name} | {count} | {status} |\n")
        f.write("\n---\n\n")
        
        # Szczegóły
        f.write("## 🔍 Szczegółowe dowody dla każdej procedury\n\n")
        
        for proc_name in sorted(by_procedure.keys(), key=lambda x: len(by_procedure[x]), reverse=True):
            proc_evidence = by_procedure[proc_name]
            
            f.write(f"### 💊 {proc_name.upper()}\n\n")
            f.write(f"**Liczba zaprzeczeń pacjenta:** {len(proc_evidence)}\n\n")
            
            f.write("| Data/Czas | Źródło | Fraza | Pełny cytat |\n")
            f.write("|-----------|--------|-------|-------------|\n")
            
            for e in sorted(proc_evidence, key=lambda x: x.timestamp)[:10]:
                f.write(f"| {e.timestamp.strftime('%Y-%m-%d %H:%M')} | {e.source} | \"{e.denial_phrase}\" | {e.full_quote[:60]}... |\n")
            
            f.write("\n")
            f.write("> **[AKCJA]** Sprawdzić Kartę Wypisową i rozliczenie NFZ dla tej procedury.\n\n")
            f.write("---\n\n")
        
        # Kwalifikacja prawna
        f.write("## ⚖️ Kwalifikacja prawna\n\n")
        f.write("Jeśli szpital rozliczył z NFZ procedury, które faktycznie nie zostały wykonane:\n\n")
        f.write("| Czyn | Podstawa prawna |\n")
        f.write("|------|----------------|\n")
        f.write("| Wyłudzenie środków publicznych | **Art. 286 § 1 KK** (oszustwo) |\n")
        f.write("| Poświadczenie nieprawdy | **Art. 271 § 1 KK** (fałsz intelektualny) |\n")
        f.write("| Nierzetelne prowadzenie dokumentacji | **Art. 41 Ustawy o prawach pacjenta** |\n\n")
        f.write("> [!IMPORTANT]\n")
        f.write("> Art. 286 KK to ściganie Z URZĘDU. Jeśli prokurator uzna, że doszło do wyłudzenia - wszczyna śledztwo niezależnie od woli pokrzywdzonego.\n")
    
    print(f"✅ Raport NFZ zapisany: {output_path}")

def main():
    base_path = Path(r"C:\Users\micha\.gemini\antigravity\PROJEKT POZEW")
    
    print("💰 AGENT WERYFIKATOR NFZ - Fraud Hunter")
    print("=" * 50)
    
    print("🔍 Szukam dowodów na niewykonane procedury...")
    evidence = scan_for_denial_phrases(base_path)
    print(f"   Znaleziono: {len(evidence)} potencjalnych zaprzeczeń")
    
    # Unikalne procedury
    unique_procs = set(e.procedure_name for e in evidence)
    print(f"   Dotyczą: {len(unique_procs)} typów procedur")
    
    # Generuj raport
    output_path = base_path / "RAPORT_WYLUDZENIA_NFZ.md"
    generate_fraud_report(evidence, output_path)
    
    print("\n" + "=" * 50)
    print("✅ ZAKOŃCZONO")

if __name__ == "__main__":
    main()
