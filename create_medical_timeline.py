
import json
import os
from datetime import datetime

base_path = r'c:\Users\micha\.gemini\antigravity\PROJEKT POZEW\your_facebook_activity\messages\inbox'
output_file = r'c:\Users\micha\.gemini\antigravity\PROJEKT POZEW\MEDYCZNA_LINIA_CZASU_MESSENGER.md'

relevant_threads = [
    'kacperdrewniak_2173539216268086',
    'bogusiaptak_3139495316380919',
    '9052962828108059',
    'dziwniludzie_6103258886383503'
]

all_messages = []

def decode_messenger_text(text):
    if not text: return ""
    try:
        # Messenger uses a weird encoding for non-ASCII
        return text.encode('latin1').decode('utf8')
    except:
        return text

for thread in relevant_threads:
    thread_path = os.path.join(base_path, thread)
    # Some threads might have multiple message_X.json files
    if not os.path.exists(thread_path):
        continue
    
    for file in os.listdir(thread_path):
        if file.startswith('message_') and file.endswith('.json'):
            file_path = os.path.join(thread_path, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                thread_name = decode_messenger_text(data.get('title', thread))
                for msg in data.get('messages', []):
                    ts = msg.get('timestamp_ms')
                    if not ts: continue
                    
                    dt = datetime.fromtimestamp(ts / 1000.0)
                    # Filter for the relevant period
                    if dt.year == 2023 and dt.month in [4, 5, 6]:
                        content = decode_messenger_text(msg.get('content', ''))
                        sender = decode_messenger_text(msg.get('sender_name', 'Unknown'))
                        
                        if not content:
                            if 'photos' in msg: content = f"[Zdjęcie: {len(msg['photos'])}]"
                            elif 'videos' in msg: content = f"[Wideo: {len(msg['videos'])}]"
                            elif 'sticker' in msg: content = "[Naklejka]"
                            else: content = "[Inna zawartość]"
                            
                        all_messages.append({
                            'ts': ts,
                            'dt_str': dt.strftime('%Y-%m-%d %H:%M:%S'),
                            'date': dt.strftime('%Y-%m-%d'),
                            'sender': sender,
                            'content': content,
                            'thread': thread_name
                        })

# Sort all messages chronologically
all_messages.sort(key=lambda x: x['ts'])

with open(output_file, 'w', encoding='utf-8') as f:
    f.write("# Medyczna Linia Czasu - Messenger (Wyselekcjonowane wątki)\n\n")
    f.write("Wątki: Kacper Drewniak, Bogusia Ptak, Grupa 9052962828108059, Dziwni Ludzie\n\n")
    
    current_date = ""
    for msg in all_messages:
        if msg['date'] != current_date:
            current_date = msg['date']
            f.write(f"\n## {current_date}\n\n")
        
        f.write(f"- **[{msg['dt_str']}] {msg['sender']}** ({msg['thread']}): {msg['content']}\n")

print(f"Extraction complete. Timeline saved to {output_file}.")
