# Translate Arabic PDF to English — Local Workflow

A single Python script that automates the full pipeline:

```
Arabic PDF → OCR → Extract Text → Chunk → Translate → English text file
```

---

## 1. Install prerequisites

### Python packages
```bash
pip install ocrmypdf pypdf deep-translator tqdm
```

### Tesseract OCR + Arabic language data

| OS | Command |
|----|---------|
| Ubuntu / Debian | `sudo apt install tesseract-ocr tesseract-ocr-ara` |
| macOS | `brew install tesseract tesseract-lang` |
| Windows | [Download installer](https://github.com/UB-Mannheim/tesseract/wiki) and tick **Arabic** during setup |

---

## 2. Run the script

```bash
python translate_arabic_pdf.py my_document.pdf
```

Default output folder: `./output/`

---

## 3. Options

| Flag | Default | Description |
|------|---------|-------------|
| `--out-dir PATH` | `output` | Where to save all output files |
| `--chunk-size N` | `4000` | Characters per translation chunk |
| `--skip-ocr` | off | Skip OCR if text is already selectable in the PDF |
| `--pause SECONDS` | `1.0` | Delay between Google Translate API calls |

### Example: already-searchable PDF, custom output folder
```bash
python translate_arabic_pdf.py book.pdf --skip-ocr --out-dir book_output
```

---

## 4. Output files

```
output/
├── searchable.pdf         ← OCR'd PDF with selectable Arabic text
├── arabic_full.txt        ← all extracted Arabic text
├── chunks/
│   ├── chunk_0001.txt
│   ├── chunk_0002.txt
│   └── ...
├── translated/
│   ├── chunk_0001_en.txt
│   ├── chunk_0002_en.txt
│   └── ...
└── english_full.txt       ← final merged English translation
```

---

## 5. Tips for 800-page documents

- **Resume support**: if the script stops mid-way, re-run it. Already-translated chunks are skipped automatically.
- **Rate limiting**: increase `--pause` (e.g. `--pause 2`) if you get Google Translate errors.
- **Quality**: the free Google Translate API gives decent results for Arabic→English. For higher quality, replace the `GoogleTranslator` call with the DeepL or OpenAI API.
- **OCR quality**: if pages are skewed or low-resolution, OCR results may be poor. Try scanning the PDF at higher DPI first.

---

## 6. Troubleshooting

| Problem | Fix |
|---------|-----|
| `tesseract not found` | Make sure Tesseract is on your PATH |
| `Arabic language data not found` | Install `tesseract-ocr-ara` (Linux) or Arabic pack (Windows) |
| Translation errors / quota exceeded | Add `--pause 3` or run in smaller batches |
| No text extracted after OCR | PDF may be very low quality; try a higher-DPI scan |
