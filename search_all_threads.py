#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skrypt do przeszukiwania WSZYSTKICH wątków Messenger w poszukiwaniu
wiadomości medycznych/dowodowych z okresu hospitalizacji (kwiecień-czerwiec 2023).

Generuje:
1. found_medical_messages.json - wszystkie znalezione wiadomości per dzień
2. found_threads_summary.md - podsumowanie wątków z dowodami
"""

import os
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# === KONFIGURACJA ===
BASE_PATH = Path(r'c:\Users\micha\.gemini\antigravity\PROJEKT POZEW\your_facebook_activity\messages\inbox')
OUTPUT_JSON = Path(r'c:\Users\micha\.gemini\antigravity\PROJEKT POZEW\found_medical_messages.json')
OUTPUT_MD = Path(r'c:\Users\micha\.gemini\antigravity\PROJEKT POZEW\found_threads_summary.md')

START_DATE = datetime(2023, 4, 1)
END_DATE = datetime(2023, 6, 30)

# Słowa kluczowe medyczne (polskie)
MEDICAL_KEYWORDS = [
    # Ból i cierpienie
    'ból', 'boli', 'bolało', 'cierpię', 'cierpienie', 'nie wytrzymam', 'umierać', 'umrę',
    # Szpital
    'szpital', 'lekarz', 'doktor', 'pielęgniarka', 'ordynator', 'obchód',
    # Procedury
    'operacja', 'zabieg', 'dren', 'drenaż', 'sączek', 'opatrunek', 'znieczulenie', 'narkoza',
    # Diagnoza
    'ropień', 'przetoka', 'crohn', 'zapalenie', 'infekcja', 'bakteria', 'sepsa', 'zakażenie',
    # Badania
    'tk', 'tomografia', 'rtg', 'usg', 'badanie', 'wynik', 'posiew',
    # Jedzenie/dieta
    'głód', 'głodny', 'jedzenie', 'dieta', 'nutri', 'nutridrik', 'nie jem', 'zagłodzą',
    # Psychiczne
    'załamanie', 'psycholog', 'płaczę', 'nie mogę', 'nie dam rady', 'strach',
    # Leki
    'antybiotyk', 'ibuprofen', 'morfina', 'lek', 'leki', 'kroplówka',
    # Stan
    'gorączka', 'krew', 'ropa', 'wydzielina', 'wyciek', 'temperatura'
]

# Słowa kluczowe dowodowe (potencjalne zaniechania)
EVIDENCE_KEYWORDS = [
    'nie przyszedł', 'nie przyszła', 'czekam', 'nikt nie', 'ignorują', 'bagatelizują',
    'błąd', 'pomyłka', 'zaniedbanie', 'zła diagnoza', 'za późno', 'dlaczego dopiero'
]

ALL_KEYWORDS = MEDICAL_KEYWORDS + EVIDENCE_KEYWORDS

def decode_messenger_text(text):
    """Dekoduje tekst z dziwnego kodowania Messengera (latin1 -> utf8)."""
    if not text:
        return ""
    try:
        return text.encode('latin1').decode('utf8')
    except (UnicodeDecodeError, UnicodeEncodeError):
        return text

def contains_keyword(text, keywords):
    """Sprawdza czy tekst zawiera słowo kluczowe (case-insensitive)."""
    if not text:
        return False, []
    text_lower = text.lower()
    found = [kw for kw in keywords if kw.lower() in text_lower]
    return len(found) > 0, found

def process_thread(thread_path):
    """Przetwarza pojedynczy wątek Messenger."""
    messages = []
    thread_name = thread_path.name
    
    for file in thread_path.iterdir():
        if file.name.startswith('message_') and file.suffix == '.json':
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    thread_title = decode_messenger_text(data.get('title', thread_name))
                    
                    for msg in data.get('messages', []):
                        ts = msg.get('timestamp_ms')
                        if not ts:
                            continue
                        
                        dt = datetime.fromtimestamp(ts / 1000.0)
                        if not (START_DATE <= dt <= END_DATE):
                            continue
                        
                        content = decode_messenger_text(msg.get('content', ''))
                        
                        # Sprawdź słowa kluczowe
                        has_keyword, found_keywords = contains_keyword(content, ALL_KEYWORDS)
                        if has_keyword:
                            sender = decode_messenger_text(msg.get('sender_name', 'Unknown'))
                            
                            messages.append({
                                'timestamp': ts,
                                'datetime': dt.strftime('%Y-%m-%d %H:%M:%S'),
                                'date': dt.strftime('%Y-%m-%d'),
                                'time': dt.strftime('%H:%M'),
                                'sender': sender,
                                'content': content,
                                'thread': thread_title,
                                'thread_id': thread_name,
                                'keywords': found_keywords
                            })
            except Exception as e:
                print(f"⚠️ Błąd w {file}: {e}")
    
    return messages

def main():
    print("🔍 Rozpoczynam przeszukiwanie WSZYSTKICH wątków Messenger...")
    print(f"📅 Okres: {START_DATE.date()} do {END_DATE.date()}")
    print(f"🔤 Słów kluczowych: {len(ALL_KEYWORDS)}")
    print()
    
    all_messages = []
    threads_with_hits = defaultdict(int)
    
    # Iteruj przez wszystkie wątki
    threads = [d for d in BASE_PATH.iterdir() if d.is_dir()]
    print(f"📂 Znaleziono {len(threads)} wątków do przeszukania")
    print()
    
    for thread_path in threads:
        messages = process_thread(thread_path)
        if messages:
            all_messages.extend(messages)
            threads_with_hits[thread_path.name] = len(messages)
            print(f"✅ {thread_path.name}: {len(messages)} wiadomości")
    
    # Sortuj chronologicznie
    all_messages.sort(key=lambda x: x['timestamp'])
    
    # Grupuj po dniach
    daily_messages = defaultdict(list)
    for msg in all_messages:
        daily_messages[msg['date']].append(msg)
    
    # === ZAPIS JSON ===
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'generated': datetime.now().isoformat(),
                'period': f"{START_DATE.date()} - {END_DATE.date()}",
                'keywords_count': len(ALL_KEYWORDS),
                'total_messages': len(all_messages),
                'threads_searched': len(threads),
                'threads_with_hits': len(threads_with_hits)
            },
            'by_date': dict(daily_messages),
            'threads_summary': dict(threads_with_hits)
        }, f, ensure_ascii=False, indent=2)
    
    # === ZAPIS MD ===
    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write("# 🔍 Wyniki Przeszukania Wszystkich Wątków Messenger\n\n")
        f.write(f"**Wygenerowano:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"**Okres:** {START_DATE.date()} do {END_DATE.date()}\n\n")
        f.write(f"**Wątków przeszukanych:** {len(threads)}\n\n")
        f.write(f"**Wątków z trafieniami:** {len(threads_with_hits)}\n\n")
        f.write(f"**Wiadomości znalezionych:** {len(all_messages)}\n\n")
        
        f.write("---\n\n## 📊 Wątki z Największą Liczbą Trafień\n\n")
        f.write("| Wątek | Liczba wiadomości |\n|:------|------------------:|\n")
        for thread, count in sorted(threads_with_hits.items(), key=lambda x: -x[1])[:15]:
            f.write(f"| `{thread}` | {count} |\n")
        
        f.write("\n---\n\n## 📅 Wiadomości Per Dzień\n\n")
        for date in sorted(daily_messages.keys()):
            msgs = daily_messages[date]
            f.write(f"### {date} ({len(msgs)} wiadomości)\n\n")
            f.write("| Godz. | Nadawca | Treść | Wątek | Słowa kluczowe |\n")
            f.write("|:------|:--------|:------|:------|:---------------|\n")
            for msg in msgs[:30]:  # Limit 30 per dzień w markdown
                content_short = msg['content'][:100].replace('\n', ' ').replace('|', '\\|')
                if len(msg['content']) > 100:
                    content_short += "..."
                keywords = ', '.join(msg['keywords'][:3])
                f.write(f"| {msg['time']} | {msg['sender']} | {content_short} | {msg['thread']} | {keywords} |\n")
            if len(msgs) > 30:
                f.write(f"\n*...i {len(msgs) - 30} więcej wiadomości tego dnia*\n")
            f.write("\n")
    
    print()
    print("=" * 60)
    print(f"✅ ZAKOŃCZONO!")
    print(f"📊 Znaleziono {len(all_messages)} wiadomości w {len(threads_with_hits)} wątkach")
    print(f"📁 JSON: {OUTPUT_JSON}")
    print(f"📄 Markdown: {OUTPUT_MD}")

if __name__ == "__main__":
    main()
