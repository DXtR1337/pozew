import os
import json
import re

def parse_markdown_report(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    filename = os.path.basename(filepath)
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    date = date_match.group(1) if date_match else "Unknown"

    title_match = re.search(r'# DZIEŃ \d+:.*? - (.*)', content)
    title = title_match.group(1) if title_match else filename

    status_match = re.search(r'## 📍 Status: (.*)', content)
    status = status_match.group(1) if status_match else ""

    facts = []
    facts_section = re.search(r'## 🔴 KLUCZOWE FAKTY\n(.*?)(?=\n##)', content, re.DOTALL)
    if facts_section:
        facts_text = facts_section.group(1)
        facts = re.findall(r'\d+\. (.*)', facts_text)

    return {
        "date": date,
        "title": title,
        "status": status,
        "facts": facts,
        "content": content
    }

def parse_personnel_report(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    sections = []
    parts = re.split(r'\n## ', content)
    for part in parts:
        lines = part.split('\n')
        header = lines[0].strip()
        body = '\n'.join(lines[1:])
        sections.append({"title": header, "body": body})

    return {"sections": sections, "content": content}

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dane_dir = os.path.join(base_dir, 'dane')
    output_file = os.path.join(base_dir, 'website', 'public', 'data.json')

    data = {
        "timeline": [],
        "personnel": {},
        "evidence": []
    }

    # Process Timeline
    timeline_dir = os.path.join(dane_dir, 'raporty_dzien_po_dniu')
    if os.path.exists(timeline_dir):
        files = sorted(os.listdir(timeline_dir))
        for f in files:
            if f.endswith('.md'):
                data["timeline"].append(parse_markdown_report(os.path.join(timeline_dir, f)))

    # Process Personnel
    personnel_file = os.path.join(dane_dir, 'RAPORT_PERSONEL_I_KOMUNIKACJA.md')
    if os.path.exists(personnel_file):
        data["personnel"] = parse_personnel_report(personnel_file)
    else:
        # Fallback if somehow missing
        data["personnel"] = {"sections": [], "content": "Brak pliku raportu personelu."}

    # Process Evidence
    evidence_dir = os.path.join(dane_dir, 'sprawdzone_raporty')
    evidence_files = [
        'RAPORT_FINALNY_DOWODY_LEVEL_3.md',
        'RAPORT_FALSZERSTW_DOKUMENTACJI.md'
    ]

    for ef in evidence_files:
        path = os.path.join(evidence_dir, ef)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data["evidence"].append({
                    "filename": ef,
                    "content": f.read()
                })

    # Write to public/data.json
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Data generated at {output_file}")

if __name__ == "__main__":
    main()
