
import os
import json
from datetime import datetime

base_path = r'c:\Users\micha\.gemini\antigravity\PROJEKT POZEW\your_facebook_activity\messages\inbox'
output_file = r'c:\Users\micha\.gemini\antigravity\PROJEKT POZEW\messenger_daily_summary_all.json'

start_date = datetime(2023, 4, 1)
end_date = datetime(2023, 6, 30)

daily_messages = {}

def process_file(file_path, relative_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            messages = data.get('messages', [])
            for msg in messages:
                ts = msg.get('timestamp_ms')
                if not ts:
                    continue
                dt = datetime.fromtimestamp(ts / 1000.0)
                if start_date <= dt <= end_date:
                    date_str = dt.strftime('%Y-%m-%d')
                    if date_str not in daily_messages:
                        daily_messages[date_str] = []
                    
                    content = msg.get('content', '')
                    sender = msg.get('sender_name', 'Unknown')
                    time_str = dt.strftime('%H:%M:%S')
                    
                    # Handle cases where there is no content but there are photos/videos
                    if not content:
                        if 'photos' in msg:
                            content = f"[Photo: {len(msg['photos'])}]"
                        elif 'videos' in msg:
                            content = f"[Video: {len(msg['videos'])}]"
                        elif 'files' in msg:
                            content = f"[File: {len(msg['files'])}]"
                        elif 'audio_files' in msg:
                            content = f"[Audio: {len(msg['audio_files'])}]"
                        elif 'sticker' in msg:
                            content = "[Sticker]"
                        else:
                            content = "[No text content]"

                    daily_messages[date_str].append({
                        'time': time_str,
                        'sender': sender,
                        'content': content,
                        'source': relative_path,
                        'ts': ts
                    })
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

for root, dirs, files in os.walk(base_path):
    for file in files:
        if file.endswith('.json'):
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, base_path)
            process_file(full_path, rel_path)

# Sort messages within each day
for date in daily_messages:
    daily_messages[date].sort(key=lambda x: x['ts'])

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(daily_messages, f, ensure_ascii=False, indent=2)

print(f"Extraction complete. Grouped by day, saved to {output_file}.")
