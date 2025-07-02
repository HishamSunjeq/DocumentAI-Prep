# Step 1: File Inspection

**Purpose**: Analyze and validate documents in the `data/` folder before processing.

## What It Does

- 📄 Scans all files in `data/` folder
- 🔍 Checks file types (PDF, DOCX, PPTX)
- 📊 Analyzes file sizes and metadata
- ✅ Validates files can be processed
- 📝 Creates inspection report

## Supported File Types

| Format     | Extensions | Notes                     |
| ---------- | ---------- | ------------------------- |
| PDF        | `.pdf`     | Text and image-based PDFs |
| Word       | `.docx`    | Microsoft Word documents  |
| PowerPoint | `.pptx`    | PowerPoint presentations  |

## Output

**File**: `output/step1-metadata_data.json`

**Contains**:

- File names and sizes
- Document types and page counts
- Validation status
- Processing recommendations

## Running Individually

```bash
python inspection_agent.py
```

## Configuration

Set in `.env` file:

```ini
DATA_FOLDER_PATH=data
OUTPUT_FOLDER_PATH=output
```

## Common Issues

| Issue             | Cause                 | Solution                       |
| ----------------- | --------------------- | ------------------------------ |
| No files found    | Empty `data/` folder  | Add documents to `data/`       |
| Invalid file type | Unsupported format    | Convert to PDF/DOCX/PPTX       |
| Permission errors | File locked/protected | Close files, remove passwords  |
| Large files       | Files > 100MB         | Consider splitting large files |

## Verbose Output Example

```
📄 Processing file: business_profile.pdf
   Size: 2.5 MB
   Type: .pdf
   Pages: 15
   Status: ✅ Valid for processing

📄 Processing file: presentation.pptx
   Size: 8.1 MB
   Type: .pptx
   Slides: 25
   Status: ✅ Valid for processing
```
