# Step 2: Text Extraction (OCR)

**Purpose**: Extract readable text from documents using OCR (Optical Character Recognition) technology.

## What It Does

- 📖 Extracts text from PDF, DOCX, PPTX files
- 🖼️ Processes images within documents
- 🔤 Handles both text-based and scanned documents
- 🧹 Cleans and normalizes extracted text
- 💾 Saves text to individual files

## Technology Used

- **PDFPlumber**: For text-based PDFs
- **Tesseract OCR**: For image-based content
- **Python-docx**: For Word documents
- **Python-pptx**: For PowerPoint files

## Input/Output

**Input**: Documents from `data/` folder
**Output**: Text files in `output/ocr_output/`

Example:

- `business_profile.pdf` → `business_profile_extracted.txt`
- `presentation.pptx` → `presentation_extracted.txt`

## Text Cleaning Features

- ✂️ Removes page numbers and headers
- 🗑️ Filters out OCR artifacts
- 📝 Normalizes whitespace and formatting
- 📧 Redacts email addresses (optional)
- 🔧 Fixes common OCR errors

## Running Individually

```bash
python OCR_Extractor.py
```

## Configuration

Set in `.env` file:

```ini
OCR_OUTPUT_FOLDER_PATH=output/ocr_output
CLEAN_EXTRACTED_TEXT=true
VERBOSE_OUTPUT=true
```

## Performance Tips

| File Type  | Processing Speed | Quality      |
| ---------- | ---------------- | ------------ |
| Text PDFs  | ⚡ Very Fast     | 🟢 Excellent |
| Image PDFs | 🐌 Slow          | 🟡 Good      |
| DOCX files | ⚡ Fast          | 🟢 Excellent |
| PPTX files | 🔄 Medium        | 🟡 Good      |

## Troubleshooting

| Problem           | Solution                                        |
| ----------------- | ----------------------------------------------- |
| No text extracted | Check if file is image-based, install Tesseract |
| Garbled text      | File may be corrupted or password-protected     |
| Slow processing   | Large image files take time, consider resizing  |
| Memory errors     | Process files individually for large documents  |

## Verbose Output Example

```
⚙️ Processing file: business_profile.pdf
ℹ️ Using direct text extraction method
✅ Extracted 2,547 words from business_profile.pdf
⚙️ Processing file: scanned_document.pdf
ℹ️ Using OCR method (image-based PDF)
⚠️ OCR processing may take longer...
✅ Extracted 1,832 words from scanned_document.pdf
```

## Quality Indicators

- **Word Count**: Higher usually indicates better extraction
- **Character Count**: Should be reasonable for document size
- **Processing Method**: Direct extraction > OCR for speed/accuracy
