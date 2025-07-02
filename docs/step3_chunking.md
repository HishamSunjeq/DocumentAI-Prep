# Step 3: Text Chunking & Embeddings

**Purpose**: Split extracted text into manageable chunks and create vector embeddings for semantic search.

## What It Does

- ✂️ Splits long texts into smaller, meaningful chunks
- 🧠 Generates vector embeddings for each chunk
- 💾 Saves chunks with embeddings to JSON files
- 🔍 Enables semantic search capabilities
- ⚡ Optimizes for AI processing

## Why Chunking?

| Benefit               | Explanation                                     |
| --------------------- | ----------------------------------------------- |
| **Model Limits**      | AI models have token limits (usually 2000-4000) |
| **Better Focus**      | Smaller chunks = more precise responses         |
| **Faster Processing** | Parallel processing of chunks                   |
| **Memory Efficiency** | Reduces computational overhead                  |

## Embedding Options

### 1. Sentence Transformers (Default)

- ✅ **Fast**: Local processing
- ✅ **Free**: No API costs
- ✅ **Offline**: Works without internet
- 📊 **Quality**: Good for most use cases

### 2. Ollama Embeddings

- 🎯 **Customizable**: Use specific models
- 🌐 **Requires**: Ollama server running
- ⚡ **GPU**: Can leverage GPU acceleration

## Input/Output

**Input**: Text files from `output/ocr_output/`
**Output**: JSON files in `output/chunked_output/`

## File Structure

```json
{
  "source_file": "business_profile_extracted.txt",
  "chunks": [
    {
      "chunk_id": "chunk_0",
      "text": "Bayanat provides digital payment solutions...",
      "word_count": 150,
      "embedding": [0.1, -0.2, 0.8, ...]
    }
  ],
  "metadata": {
    "total_chunks": 15,
    "embedding_model": "all-MiniLM-L6-v2"
  }
}
```

## Running Individually

```bash
python split_text_chunks.py
```

## Configuration

Set in `.env` file:

```ini
# Chunking settings
CHUNK_SIZE=500                    # Words per chunk
CHUNK_OVERLAP=50                  # Overlap between chunks

# Embedding settings
EMBEDDING_TYPE=sentence_transformer
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2
OLLAMA_MODEL_NAME=nomic-embed-text

# Input/Output
CHUNKED_INPUT_FOLDER_PATH=output/ocr_output
CHUNKED_OUTPUT_FOLDER_PATH=output/chunked_output
```

## Performance Metrics

| Setting                       | Speed     | Memory    | Quality     |
| ----------------------------- | --------- | --------- | ----------- |
| Small chunks (100-200 words)  | ⚡ Fast   | 🟢 Low    | 🟡 Specific |
| Medium chunks (300-500 words) | 🔄 Medium | 🟡 Medium | 🟢 Balanced |
| Large chunks (500+ words)     | 🐌 Slow   | 🔴 High   | 🟡 General  |

## Troubleshooting

| Issue           | Solution                                    |
| --------------- | ------------------------------------------- |
| Out of memory   | Reduce chunk size or batch size             |
| Slow processing | Use sentence transformers instead of Ollama |
| No embeddings   | Check model installation and settings       |
| Empty chunks    | Verify text extraction worked properly      |

## Verbose Output Example

```
ℹ️ Found 5 text files to process
ℹ️ Using embedding type: SENTENCE_TRANSFORMER
ℹ️ Model: all-MiniLM-L6-v2

⚙️ Processing: business_profile_extracted.txt
📄 Created 12 chunks from 1,847 words
✅ Generated embeddings for all chunks
💾 Saved to: business_profile_extracted_vectorized_st.json

📊 Processing complete:
   - Total files: 5
   - Total chunks: 48
   - Processing time: 23.4 seconds
```
