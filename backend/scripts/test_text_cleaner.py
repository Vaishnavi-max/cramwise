from pathlib import Path

from app.extraction.text_cleaner import TextCleaner

ocr_dir = Path("uploads/temp/ocr")
clean_dir = Path("uploads/temp/cleaned")

clean_dir.mkdir(parents=True, exist_ok=True)

for txt_file in sorted(ocr_dir.glob("*.txt")):
    print(f"Cleaning {txt_file.name}...")

    text = txt_file.read_text(encoding="utf-8")
    cleaned = TextCleaner.clean(text)

    output_file = clean_dir / txt_file.name
    output_file.write_text(cleaned, encoding="utf-8")

    print(f"✓ Saved: {output_file.name}")

print("\nFinished cleaning all OCR files.")