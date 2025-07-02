# DocumentAI-Prep Project Architecture Diagram

## 🔄 Complete Pipeline Flow Diagram

[![Download Pipeline Flow Diagram](https://img.shields.io/badge/📥_Download-Pipeline_Flow_Diagram-blue?style=for-the-badge)](https://mermaid.ink/img/pako:eNqVVE1vwjAM_StRzgM6xqAf4sKQoGjbpGnauE0cTOI2HokT0mRj6vbf16R8qIDNHHrw-9n2s58zEy3HZCBJrfgGQgNLQXJfqzrYgKO1t91sFGpLxNEEYUAoIAU8_PjBxKzIpGGCUOCzgWEzA2G7PwDjE7nI5_NoLpPZxb2FnVg7-n1DLhDJHTRaYmZtaR8JrKPdEWJY_N-gNsLZMaG8Eq7lAkKpWVN-eSWMvqX1QYOjKDfvQoUCTAoqh0SpRLrCO6KZw0QZnmOTJWjnhHm6uLaRvI_eRZQZr9T2g8GCGJRMqGPjVUGwOvPaVmZx7S2K3Zk1qYyNUPVdZcyFKIX4E2KqTKOqiZnXdgWdHMaUKGlQeIEIQKK29d5nxoVsEg-KJlm2NZKQ8aUsKWYZqYE7pqNEJfUGhBBkWz9d6e7qDvZdvBJpEF3eXt_cpjN-fXNxn9wm1zf2gE45rYFO9KcCBDbB-LV8SdmjPwC9F9M-nLYLpWaE2YkiXbW1wY2N0JZ-x9Z-x-JN5eMf2r0fNAn)

```mermaid
flowchart TD
    %% Input Layer
    A[📄 Input Documents<br/>data/] --> B{📋 File Types}
    B --> B1[📄 PDF Files]
    B --> B2[📄 DOCX Files]
    B --> B3[📄 PPTX Files]

    %% Step 1: Inspection
    B1 --> C[🔍 Step 1: File Inspection<br/>inspection_agent.py]
    B2 --> C
    B3 --> C
    C --> C1[📊 Metadata Validation<br/>output/step1-metadata_data.json]

    %% Step 2: OCR
    C1 --> D[🔤 Step 2: Text Extraction<br/>OCR_Extractor.py]
    D --> D1[📝 Plain Text Files<br/>output/ocr_output/]

    %% Step 3: Chunking
    D1 --> E[✂️ Step 3: Text Chunking<br/>split_text_chunks.py]
    E --> E1{🧠 Embedding Type}
    E1 --> E2[🤖 Sentence Transformer<br/>Local Processing]
    E1 --> E3[🌐 Ollama<br/>GPU Accelerated]
    E2 --> F[📦 Chunked Text + Embeddings<br/>output/chunked_output/]
    E3 --> F

    %% Step 4: QA Generation
    F --> G[❓ Step 4: QA Generation<br/>generate_qa.py]
    G --> G1{🎮 GPU Check}
    G1 --> G2[🚀 GPU Available<br/>Fast Processing]
    G1 --> G3[🐌 CPU Fallback<br/>Slower Processing]
    G2 --> H[💬 Q&A Pairs<br/>output/qa_pairs/]
    G3 --> H

    %% Step 5: Cleaning
    H --> I[🧹 Step 5: Output Cleaning<br/>remove_metadata_fromjson.py]
    I --> J[✨ Clean Training Data<br/>output/cleaned_json_output/]

    %% Final Output
    J --> K[🎯 Final Output<br/>Training-Ready Dataset]

    %% Styling
    classDef inputFiles fill:#cce5ff,stroke:#0066cc,stroke-width:3px,color:#000000
    classDef processing fill:#e6ccff,stroke:#6600cc,stroke-width:3px,color:#000000
    classDef output fill:#ccffcc,stroke:#009900,stroke-width:3px,color:#000000
    classDef decision fill:#ffffcc,stroke:#cc9900,stroke-width:3px,color:#000000
    classDef final fill:#ffcccc,stroke:#cc0000,stroke-width:4px,color:#000000

    class A,B,B1,B2,B3 inputFiles
    class C,D,E,G,I processing
    class C1,D1,F,H,J output
    class B,E1,G1 decision
    class K final
```

## 🏗️ System Architecture Diagram

[![Download System Architecture Diagram](https://img.shields.io/badge/📥_Download-System_Architecture-green?style=for-the-badge)](https://mermaid.ink/img/pako:eNqVlU1vwjAMQP9KlPMArYABbemFIUHTtmnTtHGbOJjEbTwSJ6TJxtTuv69J-VABm7n04Pfevzc5BylajslAklrxDYQGloLkvlZ1sAFHa2-72SjUloijCcKAUEAKePjxg4lZkUnDBKHAZwPDZgbCdn8Axidykc_n0Vwms4t7CzuxdvT7hlwgkjtotMTM2tI-ElhHuyPEsPi_QW2Es2NCeSVcywWEUrOm_PJKmH1L64MGR1Fu3oUKBZgUVA6JUol0hXdEM4eJMjzHJkvQzgnzdHFtI3kfvYsoM16p7QeDOTEomVDHxquCYHXmta3M4tpbFLszb1IZG6Hqu8qYC1EK8SfEVJlGVRMzru0KOjmMKVHSoPACEYBEbeu9z4wL2SQeFE2ybGskIeNLWVLMMlIDd0xHiUrqDQghyLZ-utLd1R3su3gl0iC6vL2-uU1n_Prm4j65Ta5v7QGdcloD3ehPBQhsgvFr-ZKyR38Aei-mfThtF0rNCLMTRbpqa4ObG6Et_Y6t_Y7Fm8rHP7R7P2gS)

```mermaid
graph TB
    subgraph "🖥️ System Environment"
        subgraph "🐍 Python Environment"
            ENV[data_prep_venv/<br/>Virtual Environment]
            REQ[requirements.txt<br/>Dependencies]
        end

        subgraph "⚙️ Configuration"
            CONF[.env File<br/>Settings & GPU Config]
            BAT[🔧 Batch Scripts<br/>setup_data_prep.bat<br/>start_data_prep.bat]
        end

        subgraph "🎮 Hardware Layer"
            GPU[🎮 NVIDIA GPU<br/>CUDA Acceleration]
            CPU[💻 CPU<br/>Fallback Processing]
            MEM[🧠 RAM<br/>8GB+ Required]
        end
    end

    subgraph "📁 Data Layer"
        INPUT[📂 data/<br/>Source Documents]
        OUTPUT[📂 output/<br/>Processed Results]
        MODELS[🤖 models/<br/>AI Models Cache]

        subgraph "📊 Output Structure"
            OUT1[📋 step1-metadata_data.json]
            OUT2[📝 ocr_output/]
            OUT3[📦 chunked_output/]
            OUT4[💬 qa_pairs/]
            OUT5[✨ cleaned_json_output/]
        end
    end

    subgraph "🔧 Processing Layer"
        MAIN[🚀 main.py<br/>Pipeline Controller]

        subgraph "📝 Core Modules"
            INSP[🔍 inspection_agent.py]
            OCR[🔤 OCR_Extractor.py]
            CHUNK[✂️ split_text_chunks.py]
            QA[❓ generate_qa.py]
            CLEAN[🧹 remove_metadata_fromjson.py]
        end

        subgraph "🛠️ Utility Modules"
            FIX[🔧 fix_ollama_gpu.py]
            TEST[🧪 test_ollama_connection.py]
            TESTGPU[🎮 test_gpu_selection.py]
        end
    end

    subgraph "🤖 AI Services"
        OLLAMA[🦙 Ollama<br/>Local LLM Server]
        SENT[🧠 Sentence Transformers<br/>Embedding Models]
        TESSERACT[👁️ Tesseract OCR<br/>Text Recognition]
    end

    %% Connections
    CONF --> MAIN
    ENV --> MAIN
    INPUT --> MAIN
    MAIN --> INSP
    MAIN --> OCR
    MAIN --> CHUNK
    MAIN --> QA
    MAIN --> CLEAN

    INSP --> OUT1
    OCR --> OUT2
    CHUNK --> OUT3
    QA --> OUT4
    CLEAN --> OUT5

    OCR --> TESSERACT
    CHUNK --> SENT
    QA --> OLLAMA

    GPU --> OLLAMA
    CPU --> OLLAMA
    GPU --> SENT

    FIX --> OLLAMA
    TEST --> OLLAMA
    TESTGPU --> GPU

    %% Styling
    classDef environment fill:#e6f3ff,stroke:#0066cc,stroke-width:3px,color:#000000
    classDef data fill:#e6ffe6,stroke:#009900,stroke-width:3px,color:#000000
    classDef processing fill:#ffe6f3,stroke:#cc0066,stroke-width:3px,color:#000000
    classDef ai fill:#fff3e6,stroke:#ff6600,stroke-width:3px,color:#000000
    classDef hardware fill:#f3e6ff,stroke:#6600cc,stroke-width:3px,color:#000000

    class ENV,REQ,CONF,BAT environment
    class INPUT,OUTPUT,MODELS,OUT1,OUT2,OUT3,OUT4,OUT5 data
    class MAIN,INSP,OCR,CHUNK,QA,CLEAN,FIX,TEST,TESTGPU processing
    class OLLAMA,SENT,TESSERACT ai
    class GPU,CPU,MEM hardware
```

## 📊 Data Flow & File Structure

[![Download Data Flow Diagram](https://img.shields.io/badge/📥_Download-Data_Flow_Diagram-purple?style=for-the-badge)](https://mermaid.ink/img/pako:eNqVUk1vwjAM_StRzgO0ggFt6YUhQdO2adK0cZs4mMRtPBInpMnG1O2_r0n5UAGbufTg99n2e5BjkKLlmAwkqRXfQGhgKUjua1UHG3C09rabzUJtiTiaIAwIBaSAhx8_mJgVmTRMEAp8NjBsZiBs9wdgfCIXhTNPptOe_35-w7VQONqFjaNfHIZaLSjWgjsotMTM2tI-ElhHuyPEsPi_QW2Es2NCeSVcywWEUrOm_PJKmH1L64MGR1Fu3oUKBZgUVA6JUol0hXdEM4eJMjzHJkvQzgnzdHFtI3kfvYsoM16p7QeDOTEomVDHxquCYHXmta3M4tpbFLsza1IZG6Hqu8qYC1EK8SfEVJlGVRMzru0KOjmMKVHSoPACEYBEbeu9z4wL2SQeFE2ybGskIeNLWVLMMlIDd0xHiUrqDQghyLZ-utLd1R3su3gl0iC6vL2-uU1n_Prm4j65Ta5v7QGdcloD3ehPBQhsgvFr-ZKyR38Aei-mfThtF0rNCLMTRbpqa4ObG6Et_Y6t_Y7Fm8rHP7R7P2gS)

```mermaid
graph LR
    subgraph "📥 Input Layer"
        PDF[📄 PDF Documents]
        DOCX[📄 Word Documents]
        PPTX[📄 PowerPoint Files]
    end

    subgraph "🔄 Processing Pipeline"
        S1[🔍 Step 1<br/>Inspection]
        S2[🔤 Step 2<br/>OCR Extraction]
        S3[✂️ Step 3<br/>Text Chunking]
        S4[❓ Step 4<br/>QA Generation]
        S5[🧹 Step 5<br/>Cleaning]
    end

    subgraph "📤 Output Layer"
        META[📊 Metadata JSON]
        TEXT[📝 Text Files]
        CHUNKS[📦 Embedded Chunks]
        QA_PAIRS[💬 Q&A Pairs]
        CLEAN_DATA[✨ Clean Dataset]
    end

    %% Flow connections
    PDF --> S1
    DOCX --> S1
    PPTX --> S1

    S1 --> META
    S1 --> S2
    S2 --> TEXT
    S2 --> S3
    S3 --> CHUNKS
    S3 --> S4
    S4 --> QA_PAIRS
    S4 --> S5
    S5 --> CLEAN_DATA

    %% Styling
    classDef input fill:#cce5ff,stroke:#0066cc,stroke-width:3px,color:#000000
    classDef process fill:#e6ccff,stroke:#6600cc,stroke-width:3px,color:#000000
    classDef output fill:#ccffcc,stroke:#009900,stroke-width:3px,color:#000000

    class PDF,DOCX,PPTX input
    class S1,S2,S3,S4,S5 process
    class META,TEXT,CHUNKS,QA_PAIRS,CLEAN_DATA output
```

## 🚀 Execution Flow Diagram

[![Download Execution Flow Diagram](https://img.shields.io/badge/📥_Download-Execution_Flow-orange?style=for-the-badge)](https://mermaid.ink/img/pako:eNqVkk1vwjAMQP9KlPMArYABbemFIUHTtmnTtHGbOJjEbTwSJ6TJxtTuv69J-VABm7n04Pfevzc5BylajslAklrxDYQGloLkvlZ1sAFHa2-72SjUloijCcKAUEAKePjxg4lZkUnDBKHAZwPDZgbCdn8Axidykc_n0Vwms4t7CzuxdvT7hlwgkjtotMTM2tI-ElhHuyPEsPi_QW2Es2NCeSVcywWEUrOm_PJKmH1L64MGR1Fu3oUKBZgUVA6JUol0hXdEM4eJMjzHJkvQzgnzdHFtI3kfvYsoM16p7QeDOTEomVDHxquCYHXmta3M4tpbFLsza1IZG6Hqu8qYC1EK8SfEVJlGVRMzru0KOjmMKVHSoPACEYBEbeu9z4wL2SQeFE2ybGskIeNLWVLMMlIDd0xHiUrqDQghyLZ-utLd1R3su3gl0iC6vL2-uU1n_Prm4j65Ta5v7QGdcloD3ehPBQhsgvFr-ZKyR38Aei-mfThtF0rNCLMTRbpqa4ObG6Et_Y6t_Y7Fm8rHP7R7P2gS)

```mermaid
sequenceDiagram
    participant User
    participant Setup as setup_data_prep.bat
    participant Main as start_data_prep.bat
    participant Pipeline as main.py
    participant GPU as GPU Check
    participant Steps as Processing Steps
    participant Output as Output Files

    User->>Setup: 🔧 First-time setup
    Setup->>Setup: Install dependencies
    Setup->>Setup: Configure environment
    Setup-->>User: ✅ Setup complete

    User->>Main: 🚀 Run pipeline
    Main->>Pipeline: Execute main.py

    Pipeline->>GPU: 🎮 Check GPU status
    GPU-->>Pipeline: GPU available/CPU fallback

    Pipeline->>Steps: Step 1: File Inspection
    Steps-->>Output: metadata_data.json

    Pipeline->>Steps: Step 2: OCR Extraction
    Steps-->>Output: Text files

    Pipeline->>Steps: Step 3: Text Chunking
    Steps-->>Output: Embedded chunks

    Pipeline->>Steps: Step 4: QA Generation
    Steps-->>Output: Q&A pairs

    Pipeline->>Steps: Step 5: Cleaning
    Steps-->>Output: Clean dataset

    Pipeline-->>User: ✅ Pipeline complete
```

## 🔧 Tool Dependencies

[![Download Dependencies Diagram](https://img.shields.io/badge/📥_Download-Dependencies_Mindmap-red?style=for-the-badge)](https://mermaid.ink/img/pako:eNqVkk1vwjAMQP9KlPMArYABbemFIUHTtmnTtHGbOJjEbTwSJ6TJxtTuv69J-VABm7n04Pfevzc5BylajslAklrxDYQGloLkvlZ1sAFHa2-72SjUloijCcKAUEAKePjxg4lZkUnDBKHAZwPDZgbCdn8Axidykc_n0Vwms4t7CzuxdvT7hlwgkjtotMTM2tI-ElhHuyPEsPi_QW2Es2NCeSVcywWEUrOm_PJKmH1L64MGR1Fu3oUKBZgUVA6JUol0hXdEM4eJMjzHJkvQzgnzdHFtI3kfvYsoM16p7QeDOTEomVDHxquCYHXmta3M4tpbFLsza1IZG6Hqu8qYC1EK8SfEVJlGVRMzru0KOjmMKVHSoPACEYBEbeu9z4wL2SQeFE2ybGskIeNLWVLMMlIDd0xHiUrqDQghyLZ-utLd1R3su3gl0iC6vL2-uU1n_Prm4j65Ta5v7QGdcloD3ehPBQhsgvFr-ZKyR38Aei-mfThtF0rNCLMTRbpqa4ObG6Et_Y6t_Y7Fm8rHP7R7P2gS)

```mermaid
mindmap
  root((DocumentAI-Prep))
    🐍 Python Core
      📦 Dependencies
        🔤 pdfplumber
        📝 python-docx
        📊 python-pptx
        👁️ pytesseract
        🧠 sentence-transformers
        🌐 requests
        📋 pandas
        🔧 python-dotenv
    🤖 AI Services
      🦙 Ollama
        🎯 Mistral Model
        🎮 GPU Acceleration
      🧠 Sentence Transformers
        📊 all-MiniLM-L6-v2
        🔍 multi-qa-MiniLM-L6-cos-v1
      👁️ Tesseract OCR
        🖼️ Image Processing
        📝 Text Recognition
    🖥️ System Tools
      🎮 NVIDIA Drivers
      🔧 CUDA Toolkit
      📊 nvidia-smi
      🐚 PowerShell
```

## 📈 Performance Optimization Flow

[![Download Performance Optimization Diagram](https://img.shields.io/badge/📥_Download-Performance_Optimization-teal?style=for-the-badge)](https://mermaid.ink/img/pako:eNqVlE1vwjAMgP9KlPMArYABbemFIUHTtmnTtHGbOJjEbTwSJ6TJxtTuv69J-VABm7n04Pfevzc5BylajslAklrxDYQGloLkvlZ1sAFHa2-72SjUloijCcKAUEAKePjxg4lZkUnDBKHAZwPDZgbCdn8Axidykc_n0Vwms4t7CzuxdvT7hlwgkjtotMTM2tI-ElhHuyPEsPi_QW2Es2NCeSVcywWEUrOm_PJKmH1L64MGR1Fu3oUKBZgUVA6JUol0hXdEM4eJMjzHJkvQzgnzdHFtI3kfvYsoM16p7QeDOTEomVDHxquCYHXmta3M4tpbFLsza1IZG6Hqu8qYC1EK8SfEVJlGVRMzru0KOjmMKVHSoPACEYBEbeu9z4wL2SQeFE2ybGskIeNLWVLMMlIDd0xHiUrqDQghyLZ-utLd1R3su3gl0iC6vL2-uU1n_Prm4j65Ta5v7QGdcloD3ehPBQhsgvFr-ZKyR38Aei-mfThtF0rNCLMTRbpqa4ObG6Et_Y6t_Y7Fm8rHP7R7P2gS)

```mermaid
flowchart TD
    START[🚀 Pipeline Start] --> GPU_CHECK{🎮 GPU Available?}

    GPU_CHECK -->|Yes| GPU_PATH[🚀 GPU Accelerated Path]
    GPU_CHECK -->|No| CPU_PATH[🐌 CPU Fallback Path]

    GPU_PATH --> GPU_OCR[⚡ Fast OCR Processing]
    GPU_PATH --> GPU_EMBED[⚡ GPU Embeddings]
    GPU_PATH --> GPU_QA[⚡ GPU QA Generation]

    CPU_PATH --> CPU_OCR[🐌 Standard OCR]
    CPU_PATH --> CPU_EMBED[🐌 CPU Embeddings]
    CPU_PATH --> CPU_QA[🐌 CPU QA Generation]

    GPU_OCR --> BATCH_PROC[📊 Batch Processing]
    CPU_OCR --> BATCH_PROC

    GPU_EMBED --> PARALLEL[⚡ Parallel Processing]
    CPU_EMBED --> SERIAL[🔄 Serial Processing]

    GPU_QA --> FAST_COMPLETE[✅ Fast Completion]
    CPU_QA --> SLOW_COMPLETE[✅ Slow Completion]

    BATCH_PROC --> MONITOR[📊 Progress Monitoring]
    PARALLEL --> MONITOR
    SERIAL --> MONITOR

    MONITOR --> FAST_COMPLETE
    MONITOR --> SLOW_COMPLETE

    FAST_COMPLETE --> RESULTS[🎯 Final Results]
    SLOW_COMPLETE --> RESULTS

    %% Styling
    classDef gpu fill:#ccffcc,stroke:#009900,stroke-width:3px,color:#000000
    classDef cpu fill:#ffcccc,stroke:#cc0000,stroke-width:3px,color:#000000
    classDef process fill:#e6ccff,stroke:#6600cc,stroke-width:3px,color:#000000
    classDef result fill:#ffffcc,stroke:#cc9900,stroke-width:4px,color:#000000

    class GPU_PATH,GPU_OCR,GPU_EMBED,GPU_QA,PARALLEL,FAST_COMPLETE gpu
    class CPU_PATH,CPU_OCR,CPU_EMBED,CPU_QA,SERIAL,SLOW_COMPLETE cpu
    class BATCH_PROC,MONITOR process
    class RESULTS result
```

## 📝 Quick Reference

> **💡 Tip**: Click the **📥 Download** buttons above each diagram to get high-quality PNG images for presentations, documentation, or offline viewing!

### 🚀 Running the Pipeline

1. **Setup**: `setup_data_prep.bat` (one-time)
2. **Execute**: `start_data_prep.bat` (main pipeline)
3. **Monitor**: Check console output for progress
4. **Results**: Find outputs in `output/` folder

### 🔧 Troubleshooting Tools

- `fix_ollama_gpu.py` - Fix GPU issues
- `test_ollama_connection.py` - Test AI model
- `test_gpu_selection.py` - GPU diagnostics

### 📁 Key Directories

- `data/` - Input documents
- `output/` - All processed results
- `models/` - Cached AI models
- `docs/` - Documentation

### ⚙️ Configuration

Edit `.env` file to customize:

- AI models and settings
- GPU configuration
- Processing parameters
- Batch sizes and performance tuning
