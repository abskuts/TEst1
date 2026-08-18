#!/usr/bin/env python3
"""
translate_arabic_pdf.py
=======================
Local pipeline: Arabic PDF → OCR → extract text → chunk → translate to English.

Prerequisites (install once):
    pip install ocrmypdf pypdf deep-translator tqdm
    # Tesseract + Arabic language data:
    # Ubuntu/Debian:  sudo apt install tesseract-ocr tesseract-ocr-ara
    # macOS:          brew install tesseract tesseract-lang
    # Windows:        https://github.com/UB-Mannheim/tesseract/wiki
    #                 Add Arabic language pack during install

Usage:
    python translate_arabic_pdf.py input.pdf
    python translate_arabic_pdf.py input.pdf --out-dir my_output --chunk-size 2000
    python translate_arabic_pdf.py input.pdf --skip-ocr   # if PDF is already searchable

Outputs (in ./output/ by default):
    searchable.pdf        – OCR'd PDF with selectable Arabic text
    arabic_full.txt       – raw extracted Arabic text
    chunks/chunk_NNN.txt  – text split into manageable pieces
    translated/chunk_NNN_en.txt – English translation of each chunk
    english_full.txt      – all translated chunks joined into one file
"""

import argparse
import os
import sys
import textwrap
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Step helpers
# ---------------------------------------------------------------------------

def run_ocr(input_pdf: Path, output_pdf: Path) -> None:
    """Run OCRmyPDF with Arabic language on the input PDF."""
    try:
        import ocrmypdf
    except ImportError:
        sys.exit("ocrmypdf not installed. Run: pip install ocrmypdf")

    print(f"[1/4] Running OCR on {input_pdf} ...")
    ocrmypdf.ocr(
        str(input_pdf),
        str(output_pdf),
        language="ara",
        deskew=True,
        rotate_pages=True,
        force_ocr=True,
    )
    print(f"      Searchable PDF saved → {output_pdf}")


def extract_text(pdf_path: Path, out_txt: Path) -> str:
    """Extract text from a (searchable) PDF using pypdf."""
    try:
        from pypdf import PdfReader
    except ImportError:
        sys.exit("pypdf not installed. Run: pip install pypdf")

    print(f"[2/4] Extracting text from {pdf_path} ...")
    reader = PdfReader(str(pdf_path))
    pages_text = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages_text.append(text)
        if i % 50 == 0:
            print(f"      Processed page {i}/{len(reader.pages)}")

    full_text = "\n\n".join(pages_text)
    out_txt.write_text(full_text, encoding="utf-8")
    print(f"      Arabic text saved → {out_txt}  ({len(full_text):,} chars)")
    return full_text


def chunk_text(text: str, chunk_dir: Path, chunk_size: int) -> list[Path]:
    """Split text into chunks of ~chunk_size characters, breaking on whitespace."""
    chunk_dir.mkdir(parents=True, exist_ok=True)
    words = text.split()
    chunks, current, current_len = [], [], 0
    for word in words:
        wlen = len(word) + 1
        if current_len + wlen > chunk_size and current:
            chunks.append(" ".join(current))
            current, current_len = [], 0
        current.append(word)
        current_len += wlen
    if current:
        chunks.append(" ".join(current))

    paths = []
    for idx, chunk in enumerate(chunks, start=1):
        p = chunk_dir / f"chunk_{idx:04d}.txt"
        p.write_text(chunk, encoding="utf-8")
        paths.append(p)

    print(f"[3/4] Split into {len(paths)} chunks → {chunk_dir}")
    return paths


def translate_chunks(
    chunk_paths: list[Path],
    out_dir: Path,
    pause: float = 1.0,
) -> Path:
    """Translate each chunk from Arabic to English using deep-translator (Google)."""
    try:
        from deep_translator import GoogleTranslator
    except ImportError:
        sys.exit("deep-translator not installed. Run: pip install deep-translator")

    try:
        from tqdm import tqdm
        iterator = tqdm(chunk_paths, desc="Translating", unit="chunk")
    except ImportError:
        iterator = chunk_paths

    out_dir.mkdir(parents=True, exist_ok=True)
    translator = GoogleTranslator(source="ar", target="en")
    translated_paths = []

    for chunk_path in iterator:
        out_path = out_dir / chunk_path.name.replace(".txt", "_en.txt")
        if out_path.exists():
            # Resume support: skip already-translated chunks
            translated_paths.append(out_path)
            continue

        arabic_text = chunk_path.read_text(encoding="utf-8")
        # Google Translate free API has a ~5000 char limit per call
        if len(arabic_text) > 4900:
            # Sub-chunk if needed
            sub_chunks = textwrap.wrap(arabic_text, 4900, break_long_words=False)
        else:
            sub_chunks = [arabic_text]

        english_parts = []
        for sub in sub_chunks:
            try:
                english_parts.append(translator.translate(sub))
                time.sleep(pause)
            except Exception as exc:
                print(f"\n  Warning: translation failed for a sub-chunk: {exc}")
                english_parts.append(f"[TRANSLATION ERROR: {exc}]\n{sub}")

        out_path.write_text("\n".join(english_parts), encoding="utf-8")
        translated_paths.append(out_path)

    print(f"[4/4] Translations saved → {out_dir}")
    return out_dir


def merge_translations(translated_dir: Path, out_file: Path) -> None:
    """Join all translated chunks into one file."""
    parts = sorted(translated_dir.glob("*_en.txt"))
    combined = "\n\n".join(p.read_text(encoding="utf-8") for p in parts)
    out_file.write_text(combined, encoding="utf-8")
    print(f"      Full English text → {out_file}  ({len(combined):,} chars)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert an Arabic PDF to English via OCR + translation."
    )
    parser.add_argument("input_pdf", help="Path to the Arabic PDF file")
    parser.add_argument(
        "--out-dir", default="output", help="Output directory (default: ./output)"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=4000,
        help="Characters per text chunk (default: 4000)",
    )
    parser.add_argument(
        "--skip-ocr",
        action="store_true",
        help="Skip OCR step if PDF already has selectable text",
    )
    parser.add_argument(
        "--pause",
        type=float,
        default=1.0,
        help="Seconds to pause between translation API calls (default: 1.0)",
    )
    args = parser.parse_args()

    input_pdf = Path(args.input_pdf).resolve()
    if not input_pdf.exists():
        sys.exit(f"File not found: {input_pdf}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    searchable_pdf = out_dir / "searchable.pdf"
    arabic_txt = out_dir / "arabic_full.txt"
    chunk_dir = out_dir / "chunks"
    translated_dir = out_dir / "translated"
    english_full = out_dir / "english_full.txt"

    # 1. OCR
    if args.skip_ocr:
        searchable_pdf = input_pdf
        print("[1/4] Skipping OCR (--skip-ocr set).")
    else:
        run_ocr(input_pdf, searchable_pdf)

    # 2. Extract text
    full_arabic = extract_text(searchable_pdf, arabic_txt)

    # 3. Chunk
    chunk_paths = chunk_text(full_arabic, chunk_dir, args.chunk_size)

    # 4. Translate
    translate_chunks(chunk_paths, translated_dir, pause=args.pause)

    # 5. Merge
    merge_translations(translated_dir, english_full)

    print("\nDone! Final output:")
    print(f"  Arabic text :  {arabic_txt}")
    print(f"  English text:  {english_full}")


if __name__ == "__main__":
    main()
