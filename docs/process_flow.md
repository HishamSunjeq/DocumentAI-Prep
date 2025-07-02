
# Data Preparation Pipeline Flow

## Overview
Transform business documents into AI-ready question-answer pairs through 5 automated steps.

## Complete Process Flow

### Step 1: File Inspection
**Script**: `inspection_agent.py`
**Input**: Documents in `data/` folder (PDF, DOCX, PPTX)
**Output**: File metadata and validation report (`output/step1-metadata_data.json`)
**Purpose**: Validate files before processing

### Step 2: Text Extraction (OCR)
**Script**: `OCR_Extractor.py`  
**Input**: Source documents from `data/`
**Output**: Plain text files (`output/ocr_output/`)
**Purpose**: Extract readable text using OCR technology

### Step 3: Text Chunking & Embeddings
**Script**: `split_text_chunks.py`
**Input**: Extracted text files
**Output**: Chunked text with vector embeddings (`output/chunked_output/`)
**Purpose**: Split text into AI-processable chunks with semantic embeddings

### Step 4: QA Generation
**Script**: `generate_qa.py`
**Input**: Chunked text with embeddings  
**Output**: Question-answer pairs (`output/qa_pairs/`)
**Purpose**: Generate training data using AI language models

### Step 5: Output Cleaning (Optional)
**Script**: `remove_metadata_fromjson.py`
**Input**: Q&A pairs with metadata
**Output**: Clean prompt-response pairs (`output/cleaned_json_output/`)
**Purpose**: Create training-ready datasets

## Quick Start Commands

**Full Pipeline**: `start_data_prep.bat`
**Individual Steps**: `python [script_name].py`
**Configuration**: Edit `.env` file

## Data Flow Diagram

```
Documents (data/) 
    ↓ [Step 1: Inspection]
File Metadata (output/)
    ↓ [Step 2: OCR]  
Text Files (output/ocr_output/)
    ↓ [Step 3: Chunking]
Chunked Text + Embeddings (output/chunked_output/)
    ↓ [Step 4: QA Generation]
Q&A Pairs with Metadata (output/qa_pairs/)
    ↓ [Step 5: Cleaning]
Clean Q&A Pairs (output/cleaned_json_output/)
```

For detailed information about each step, see the individual step documentation in the `docs/` folder.