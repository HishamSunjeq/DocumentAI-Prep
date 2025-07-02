# Setup Guide

## System Requirements

- **Windows 10/11**
- **Python 3.8+** with pip
- **4GB free disk space**
- **8GB RAM minimum**

## Quick Setup

1. **Run the setup script**:

   ```
   setup_data_prep.bat
   ```

   if update didnt start automaticly, you can run the script again, and chose option 1 (update) to install all requirements.

2. **Wait for completion** (may take 5-10 minutes)

3. **Verify setup** by running:
   ```
   start_data_prep.bat
   ```

## What the Setup Does

- ✅ Creates Python virtual environment
- ✅ Installs all required packages
- ✅ Downloads and configures Tesseract OCR
- ✅ Sets up default configuration
- ✅ Creates output directories

## Manual Setup (If Automatic Fails)

```powershell
# Create virtual environment
python -m venv data_prep_venv

# Activate environment
.\data_prep_venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt

# Create output directories
mkdir output\ocr_output
mkdir output\chunked_output
mkdir output\qa_pairs
```

## Tesseract OCR Installation

If OCR fails during document processing:

1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to default location: `C:\Program Files\Tesseract-OCR\`
3. Verify by running: `tesseract --version`

## GPU Setup (Optional)

For faster processing with NVIDIA GPUs:

1. Install CUDA drivers from NVIDIA
2. Run: `python fix_ollama_gpu.py`
3. Follow the on-screen instructions

## Configuration

Edit `.env` file for customization:

```ini
# Basic settings
QA_PAIRS_PER_CHUNK=3
EMBEDDING_TYPE=sentence_transformer

# Advanced settings
QA_BATCH_SIZE=5
GPU_DEVICE_ID=0
VERBOSE_OUTPUT=true
```

## Troubleshooting

| Problem           | Solution                      |
| ----------------- | ----------------------------- |
| Python not found  | Add Python to system PATH     |
| Permission errors | Run as administrator          |
| Network errors    | Check firewall/proxy settings |
| Disk space        | Free up at least 4GB          |

## Verification

After setup, you should have:

- ✅ `data_prep_venv/` folder
- ✅ All packages installed without errors
- ✅ Tesseract working (`tesseract --version`)
- ✅ Configuration file (`.env`)
