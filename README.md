# Bayanat Data Preparation & QA Generation Pipeline

A complete, GPU-accelerated pipeline for processing business documents and generating high-quality question-answer pairs for chatbot training.

# 📚 Document AI Prep

## Installation & Setup

### Setup guide: [Setup Guide](docs/setup_guide.md)

## 🚀 Quick Start

# Clone the repository

1. **Setup** (First time only):

   ```
   setup_data_prep.bat
   ```

2. **Run Pipeline** (With detailed output):

   ```
   start_data_prep.bat
   ```

3. **Place your documents** in the `data/` folder (PDF, DOCX, PPTX)

4. **Get results** from the `output/` folder

## 📁 Project Structure

```
├── data/                     # Your source documents (PDF, DOCX, PPTX)
├── output/                   # All processed results
│   ├── ocr_output/          # Extracted text files
│   ├── chunked_output/      # Text chunks with embeddings
│   └── qa_pairs/            # Generated Q&A pairs
├── docs/                    # Process documentation
├── setup_data_prep.bat     # One-time setup script
└── start_data_prep.bat  # Run with detailed output
```

## 📜 Full diagram: [Project Diagram](docs/project_diagram.md)

## 🔄 Pipeline Steps

| Step | Process             | Input                | Output                                                  |
| ---- | ------------------- | -------------------- | ------------------------------------------------------- |
| 1    | **File Inspection** | Documents in `data/` | File metadata & validation                              |
| 2    | **Text Extraction** | Source documents     | Plain text files (`output/ocr_output/`)                 |
| 3    | **Text Chunking**   | Extracted text       | Chunked text with embeddings (`output/chunked_output/`) |
| 4    | **QA Generation**   | Text chunks          | Question-answer pairs (`output/qa_pairs/`)              |
| 5    | **Clean Output**    | QA pairs             | Cleaned prompt-response pairs                           |

## ⚙️ Configuration

Edit the `.env` file to customize settings:

```ini
# AI Model Settings
QA_OLLAMA_MODEL=mistral           # AI model for QA generation
QA_PAIRS_PER_CHUNK=3              # Number of Q&A pairs per text chunk

# Processing Settings
EMBEDDING_TYPE=sentence_transformer  # ollama or sentence_transformer
QA_BATCH_SIZE=5                   # Processing batch size

# GPU Settings (if available)
GPU_DEVICE_ID=0                   # Which GPU to use
```

## 🛠️ Individual Tools

You can also run individual steps:

```bash
# Run specific pipeline steps
python main.py                    # Full pipeline
python inspection_agent.py        # Step 1: File inspection
python OCR_Extractor.py           # Step 2: Text extraction
python split_text_chunks.py       # Step 3: Text chunking
python generate_qa.py             # Step 4: QA generation
python remove_metadata_fromjson.py # Step 5: Clean output

# Troubleshooting
python fix_ollama_gpu.py          # Fix GPU issues
python test_ollama_connection.py  # Test AI model connection
```

## 📊 Output Examples

**Input**: Business document (PDF/DOCX/PPTX)
**Output**: JSON file with Q&A pairs:

```json
[
  {
    "prompt": "",
    "response": "",
    "source_file": "file.pdf",
    "chunk_id": "chunk_1"
  }
]
```

## 🔍 Verbose Mode Features

When using `start_data_prep.bat`, you'll see:

- ✅ **File-by-file processing status**
- 📊 **Real-time progress updates**
- ⚡ **Performance statistics**
- 🎮 **GPU utilization metrics**
- 📈 **Word counts and processing times**

Perfect for troubleshooting and optimization!

## 🚨 Troubleshooting

| Issue               | Solution                                              |
| ------------------- | ----------------------------------------------------- |
| **Setup fails**     | Run as administrator, check Python installation       |
| **No GPU detected** | Run `python fix_ollama_gpu.py`                        |
| **OCR errors**      | Install Tesseract OCR (included in setup)             |
| **Model errors**    | Check internet connection, verify Ollama installation |
| **Empty outputs**   | Check `data/` folder has supported file formats       |

## 📋 System Requirements

- **OS**: Windows 10/11
- **Python**: 3.8 or higher
- **RAM**: 8GB minimum, 16GB recommended
- **GPU**: NVIDIA GPU recommended for faster processing
- **Storage**: 2GB free space

## 🤝 Support

- Check `docs/` folder for detailed guides
- Run verbose mode for detailed error messages
- Ensure all requirements are installed via setup script

---