import fitz  # PyMuPDF
import os

# Lista plików PDF do przetworzenia
pdf_files = [
    "DZIECI-2023-24_ofUNIQA (1).pdf",
    "DZIECI-2023-24_ofUNIQA-OWU (1).pdf",
    "GENERALI NNW karta produktu2022 copy.pdf",
    "GENERALI NNW OWU2022.pdf",
    "polisa_100072958825 (1).pdf",
    "WIENCEK Janusz NNW2023synMichał (1).pdf"
]

base_dir = r"c:\Users\micha\.gemini\antigravity\PROJEKT POZEW\02_DOWODY_I_TRANSKRYPCJE\ubezpieczyciel"

for pdf_file in pdf_files:
    pdf_path = os.path.join(base_dir, pdf_file)
    output_path = os.path.join(base_dir, pdf_file.replace(".pdf", "_OCR.txt"))
    
    if not os.path.exists(pdf_path):
        print(f"BRAK: {pdf_file}")
        continue
    
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page_num, page in enumerate(doc, 1):
            page_text = page.get_text()
            if page_text.strip():
                text += f"\n\n--- STRONA {page_num} ---\n\n"
                text += page_text
        doc.close()
        
        if text.strip():
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"OK: {pdf_file} -> {os.path.basename(output_path)}")
        else:
            print(f"PUSTY (skan?): {pdf_file}")
    except Exception as e:
        print(f"BŁĄD: {pdf_file} - {str(e)}")

print("\nGotowe!")
