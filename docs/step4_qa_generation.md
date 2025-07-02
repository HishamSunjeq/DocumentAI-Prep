# Step 4: QA Generation

**Purpose**: Generate high-quality question-answer pairs from text chunks using AI language models.

## What It Does

- 🤖 Uses AI models (Ollama) to generate Q&A pairs
- 📝 Creates multiple questions per text chunk
- 🎯 Focuses on key information and concepts
- 📊 Monitors GPU usage and performance
- 💾 Saves Q&A pairs with metadata

## AI Models Supported

| Model         | Speed     | Quality      | Use Case                        |
| ------------- | --------- | ------------ | ------------------------------- |
| **Mistral**   | 🔄 Medium | 🟢 Excellent | General purpose, recommended    |
| **Llama2**    | 🐌 Slower | 🟢 Excellent | High-quality responses          |
| **TinyLlama** | ⚡ Fast   | 🟡 Good      | Quick testing, resource-limited |

## Input/Output

**Input**: Chunked JSON files from `output/chunked_output/`
**Output**: Q&A JSON files in `output/qa_pairs/`

## Generated Q&A Format

```json
[
  {
    "source_file": "business_profile_extracted.txt",
    "chunk_id": "chunk_0",
    "prompt": "What services does Bayanat provide?",
    "response": "Bayanat provides digital payment solutions and automated salary payment management systems for banks and financial institutions.",
    "character_count": 245,
    "word_count": 42,
    "generated_at": "2025-01-15T10:30:45"
  }
]
```

## Running Individually

```bash
python generate_qa.py
```

## Configuration

Set in `.env` file:

```ini
# Model settings
QA_OLLAMA_MODEL=mistral           # AI model to use
QA_OLLAMA_HOST=http://localhost:11434

# Generation settings
QA_PAIRS_PER_CHUNK=3              # Questions per chunk
QA_BATCH_SIZE=5                   # Chunks processed together

# Input/Output
QA_INPUT_FOLDER=output/chunked_output
QA_OUTPUT_FOLDER=output/qa_pairs

# Monitoring
QA_ENABLE_MONITORING=true         # Show detailed progress
```

## Quality Features

- 🎯 **Context-aware**: Questions relate to chunk content
- 📚 **Diverse**: Multiple question types (what, how, why)
- 🔍 **Specific**: Answers contain concrete details
- 📏 **Appropriate length**: Balanced question/answer sizes

## Performance Optimization

### GPU Usage

- **Check status**: Automatic GPU detection
- **Monitor usage**: Real-time GPU utilization
- **Auto-fix**: Runs GPU optimization if needed

### Processing Speed

| Factor           | Impact | Optimization                   |
| ---------------- | ------ | ------------------------------ |
| **Model size**   | High   | Use smaller models for testing |
| **Batch size**   | Medium | Increase for faster processing |
| **GPU memory**   | High   | Monitor and adjust batch size  |
| **Chunk length** | Low    | Longer chunks = more context   |

## Troubleshooting

| Problem               | Solution                                  |
| --------------------- | ----------------------------------------- |
| Ollama not responding | Start Ollama: `ollama serve`              |
| GPU not detected      | Run `python fix_ollama_gpu.py`            |
| Out of memory         | Reduce batch size or use smaller model    |
| Poor quality Q&A      | Try different model or adjust temperature |
| Slow generation       | Check GPU usage, reduce batch size        |

## Verbose Output Example

```
🔧 Configuration:
   Input folder: output/chunked_output
   Output folder: output/qa_pairs
   Ollama host: http://localhost:11434
   Ollama model: mistral
   Q&A pairs per chunk: 3

🔍 Testing Ollama connection and GPU usage...
📊 System stats before request:
   CPU: 25.3%
   Memory: 45.2%
   GPU 0: 15% util, 8.5% memory (1024MB/12GB)

🚀 Found 5 files to process

⚙️ Processing: business_profile_extracted_vectorized_st.json
📊 File contains 12 chunks
✅ Generated 36 Q&A pairs (3 per chunk)
⏱️ Processing time: 45.2 seconds

✅ QA generation completed in 234.7 seconds
📊 Generated 5 output files with 180 QA pairs
```
