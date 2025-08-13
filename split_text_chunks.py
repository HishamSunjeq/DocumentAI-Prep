import json
from pathlib import Path
from dotenv import load_dotenv
import os
import re
import requests
import numpy as np
import concurrent.futures
import time
from threading import Lock

# Try to import SentenceTransformers, handle gracefully if not available
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("⚠️  SentenceTransformers not available. Install with: pip install sentence-transformers")

load_dotenv()

# Configuration from environment variables
EMBEDDING_TYPE = os.getenv("EMBEDDING_TYPE", "ollama").lower()
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "nomic-embed-text:latest")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
SENTENCE_TRANSFORMER_MODEL = os.getenv("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")
MODELS_FOLDER_PATH = os.getenv("MODELS_FOLDER_PATH", "./models")

# Check for verbose mode
VERBOSE = os.getenv('VERBOSE_OUTPUT', 'false').lower() == 'true'
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

# Legacy support
CHUNKED_MODEL_NAME = os.getenv("CHUNKED_MODEL_NAME", OLLAMA_MODEL_NAME)

def log_verbose(message, level="info"):
    """Log message only if verbose mode is enabled"""
    if not VERBOSE and not DEBUG and level != "error":
        return
        
    prefix = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "debug": "🔍",
        "process": "⚙️",
        "chunk": "📄"
    }.get(level, "ℹ️")
    
    print(f"{prefix} {message}")

def get_ollama_embedding_batch(texts, model_name=os.getenv("CHUNKED_MODEL_NAME"), ollama_url="http://localhost:11434", max_workers=4):
    """Get embeddings from Ollama API in parallel for better performance 🚀"""
    
    def get_single_embedding(text_with_index):
        text, index = text_with_index
        try:
            response = requests.post(
                f"{ollama_url}/api/embeddings",
                json={
                    "model": model_name,
                    "prompt": text
                },
                timeout=30  # Add timeout to prevent hanging
            )
            if response.status_code == 200:
                return index, response.json()["embedding"]
            else:
                log_verbose(f"Ollama API error for chunk {index}: {response.status_code}", level="error")
                return index, None
        except requests.exceptions.RequestException as e:
            log_verbose(f"Connection error for chunk {index}: {e}", level="error")
            return index, None
    
    log_verbose(f"Processing {len(texts)} embeddings with {max_workers} parallel workers...", level="process")
    embeddings = [None] * len(texts)
    
    # Create list of (text, index) tuples for tracking
    indexed_texts = [(text, i) for i, text in enumerate(texts)]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_index = {
            executor.submit(get_single_embedding, text_with_index): text_with_index[1] 
            for text_with_index in indexed_texts
        }
        
        # Collect results as they complete
        completed = 0
        for future in concurrent.futures.as_completed(future_to_index):
            index, embedding = future.result()
            embeddings[index] = embedding if embedding is not None else [0.0] * 768
            completed += 1
            if completed % 5 == 0 or completed == len(texts):
                log_verbose(f"Progress: {completed}/{len(texts)} embeddings completed", level="info")
    
    return embeddings

def get_ollama_embedding(text, model_name=os.getenv("CHUNKED_MODEL_NAME"), ollama_url="http://localhost:11434"):
    """Get embeddings from Ollama API 🤖 (Single embedding - use batch function for better performance)"""
    try:
        response = requests.post(
            f"{ollama_url}/api/embeddings",
            json={
                "model": model_name,
                "prompt": text
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()["embedding"]
        else:
            log_verbose(f"Ollama API error: {response.status_code}", level="error")
            return None
    except requests.exceptions.RequestException as e:
        log_verbose(f"Connection error to Ollama: {e}", level="error")
        return None

# Global variable to cache the SentenceTransformer model
_sentence_transformer_model = None
_model_lock = Lock()

def get_sentence_transformer_model(model_name=SENTENCE_TRANSFORMER_MODEL):
    """Load and cache SentenceTransformer model from local models folder 🤖"""
    global _sentence_transformer_model
    
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        raise ImportError("SentenceTransformers not available. Install with: pip install sentence-transformers")
    
    with _model_lock:
        if _sentence_transformer_model is None:
            try:
                models_path = Path(MODELS_FOLDER_PATH)
                models_path.mkdir(parents=True, exist_ok=True)
                
                # Try to load from local models folder first
                local_model_path = models_path / model_name
                if local_model_path.exists():
                    log_verbose(f"Loading SentenceTransformer model from local path: {local_model_path}", level="process")
                    _sentence_transformer_model = SentenceTransformer(str(local_model_path))
                else:
                    log_verbose(f"Downloading SentenceTransformer model: {model_name}", level="process")
                    log_verbose(f"Saving to: {local_model_path}", level="process")
                    _sentence_transformer_model = SentenceTransformer(model_name, cache_folder=str(models_path))
                    
                log_verbose(f"SentenceTransformer model loaded successfully!", level="success")
                
            except Exception as e:
                log_verbose(f"Error loading SentenceTransformer model: {e}", level="error")
                raise
                
    return _sentence_transformer_model

def get_sentence_transformer_embedding_batch(texts, model_name=SENTENCE_TRANSFORMER_MODEL):
    """Get embeddings using SentenceTransformer in batch for maximum performance 🚀"""
    try:
        model = get_sentence_transformer_model(model_name)
        log_verbose(f"Processing {len(texts)} embeddings with SentenceTransformer...", level="process")
        
        # SentenceTransformers handles batching internally and is very efficient
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        
        log_verbose(f"Generated {len(embeddings)} embeddings!", level="success")
        return embeddings.tolist()  # Convert numpy arrays to lists for JSON serialization
        
    except Exception as e:
        log_verbose(f"Error generating SentenceTransformer embeddings: {e}", level="error")
        # Return zero embeddings as fallback
        embedding_dim = 384  # Default dimension for most sentence transformers
        return [[0.0] * embedding_dim for _ in texts]

def get_sentence_transformer_embedding(text, model_name=SENTENCE_TRANSFORMER_MODEL):
    """Get single embedding using SentenceTransformer (use batch function for better performance)"""
    try:
        model = get_sentence_transformer_model(model_name)
        embedding = model.encode([text], convert_to_numpy=True)[0]
        return embedding.tolist()
    except Exception as e:
        log_verbose(f"Error generating SentenceTransformer embedding: {e}", level="error")
        return None

def split_text_into_chunks(text, chunk_size=500, overlap=50):
    """Split text into overlapping chunks for better context preservation 📝"""
    # Clean and normalize text first
    text = re.sub(r'\s+', ' ', text.strip())  # Normalize whitespace
    words = text.split()
    
    if len(words) <= chunk_size:
        return [text]  # Return as single chunk if smaller than chunk_size
    
    chunks = []
    step_size = chunk_size - overlap
    
    for i in range(0, len(words), step_size):
        chunk_words = words[i:i + chunk_size]
        chunk_text = ' '.join(chunk_words)
        chunks.append(chunk_text)
        
        # Stop if we've reached the end
        if i + chunk_size >= len(words):
            break
    
    return chunks

def process_text_files_and_vectorize(input_dir=os.getenv("CHUNKED_INPUT_FOLDER_PATH"), output_dir=os.getenv("CHUNKED_OUTPUT_FOLDER_PATH"), embedding_type=None, model_name=None, chunk_size=500, overlap=50, max_workers=4, verbose=None):
    """Process text files, split into chunks, and transform into vector embeddings! Each file gets its own JSON! 🚀"""
    
    # Set defaults from environment if not provided
    if embedding_type is None:
        embedding_type = EMBEDDING_TYPE
    if model_name is None:
        model_name = OLLAMA_MODEL_NAME if embedding_type.lower() == "ollama" else SENTENCE_TRANSFORMER_MODEL
    if verbose is None:
        verbose = VERBOSE
    
    start_time = time.time()
    
    # Get all text files from the input directory
    input_path = Path(input_dir)
    text_files = list(input_path.glob("*.txt"))
    
    if not text_files:
        log_verbose(f"No text files found in {input_dir}", level="error")
        return []
    
    log_verbose(f"Found {len(text_files)} text files to process!")
    log_verbose(f"Using embedding type: {embedding_type.upper()}")
    log_verbose(f"Model: {model_name}")
    
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Check embedding system availability
    if embedding_type.lower() == "sentence_transformer":
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            log_verbose("SentenceTransformers not available! Install with: pip install sentence-transformers", level="error")
            return []
        try:
            # Test loading the model
            get_sentence_transformer_model(model_name)
            log_verbose(f"SentenceTransformer model ready!")
        except Exception as e:
            log_verbose(f"Error loading SentenceTransformer model: {e}", level="error")
            return []
    else:  # Ollama
        try:
            test_response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
            if test_response.status_code == 200:
                log_verbose(f"Ollama is running! Using model: {model_name}")
                log_verbose(f"Using {max_workers} parallel workers for faster processing")
            else:
                log_verbose("Ollama is not responding properly!", level="error")
                return []
        except requests.exceptions.RequestException:
            log_verbose(f"Cannot connect to Ollama! Make sure it's running on {OLLAMA_URL}", level="error")
            return []
    
    all_processed_files = []
    total_chunks_processed = 0
    
    # Process each text file separately
    for file_idx, file_path in enumerate(text_files, 1):
        log_verbose(f"\nProcessing file {file_idx}/{len(text_files)}: {file_path.name}")
        file_start_time = time.time()
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text_content = f.read()
            
            # Skip empty files
            if not text_content.strip():
                log_verbose(f"Skipping empty file: {file_path.name}", level="warning")
                continue
            
            # Split text into chunks
            log_verbose(f"Splitting text into chunks (size: {chunk_size}, overlap: {overlap})...", level="process")
            file_chunks_text = split_text_into_chunks(text_content, chunk_size, overlap)
            
            # Create chunks with metadata
            file_chunks = []
            for i, chunk_text in enumerate(file_chunks_text):
                chunk_data = {
                    "source_file": file_path.name,
                    "chunk_id": f"{file_path.stem}_chunk_{i}",
                    "chunk_index": i,
                    "text": chunk_text,
                    "character_count": len(chunk_text),
                    "word_count": len(chunk_text.split())
                }
                file_chunks.append(chunk_data)
            
            log_verbose(f"Created {len(file_chunks)} chunks from {file_path.name}", level="success")
            
            # Vectorize chunks for this file using the configured embedding method
            log_verbose("Generating embeddings... Universal magic! ✨", level="process")
            texts = [chunk["text"] for chunk in file_chunks]
            
            # Use the universal embedding function
            embeddings = get_embedding_batch(texts, embedding_type, model_name, max_workers)
            
            log_verbose(f"Generated {len(embeddings)} embeddings!", level="success")
            
            # Attach embeddings to chunks
            for i, emb in enumerate(embeddings):
                if i < len(file_chunks):  # Safety check
                    file_chunks[i]["embedding"] = emb
            
            # Save each file's chunks to its own JSON
            embedding_suffix = "ollama" if embedding_type.lower() == "ollama" else "st"
            output_filename = f"{file_path.stem}_vectorized_{embedding_suffix}.json"
            output_file_path = output_path / output_filename
            
            log_verbose("Saving vectorized chunks to JSON...", level="process")
            with open(output_file_path, "w", encoding="utf-8") as f:
                json.dump(file_chunks, f, indent=2, ensure_ascii=False)
            
            file_time = time.time() - file_start_time
            total_chunks_processed += len(file_chunks)
            
            log_verbose(f"Saved {len(file_chunks)} vectorized chunks to: {output_filename}", level="success")
            log_verbose(f"File processing time: {file_time:.2f} seconds", level="info")
            all_processed_files.append(output_file_path)
            
        except Exception as e:
            log_verbose(f"Error processing {file_path.name}: {str(e)}", level="error")
            continue
    
    total_time = time.time() - start_time
    log_verbose(f"\n🎉 WOOHOO! Processed {len(all_processed_files)} files!")
    log_verbose(f"Using {embedding_type.upper()} embeddings with model: {model_name}")
    log_verbose(f"Total chunks processed: {total_chunks_processed}")
    log_verbose(f"Total processing time: {total_time:.2f} seconds")
    log_verbose(f"Average speed: {total_chunks_processed/total_time:.1f} chunks/second")
    log_verbose("🌟 Each file now has its own vectorized JSON with your chosen embedding method!")
    
    return all_processed_files

def process_text_files_only(input_dir=os.getenv("CHUNKED_INPUT_FOLDER_PATH"), output_dir=os.getenv("CHUNKED_OUTPUT_FOLDER_PATH"), chunk_size=500, overlap=50):
    """Process text files and split into chunks WITHOUT embeddings for maximum speed! 🏃‍♂️💨"""
    
    start_time = time.time()
    
    # Get all text files from the input directory
    input_path = Path(input_dir)
    text_files = list(input_path.glob("*.txt"))
    
    if not text_files:
        log_verbose(f"No text files found in {input_dir}", level="error")
        return []
    
    log_verbose(f"Found {len(text_files)} text files to process!")
    log_verbose("Fast mode: Text chunking only (no embeddings)")
    
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    all_processed_files = []
    total_chunks_processed = 0
    
    # Process each text file separately
    for file_idx, file_path in enumerate(text_files, 1):
        log_verbose(f"\nProcessing file {file_idx}/{len(text_files)}: {file_path.name}")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text_content = f.read()
            
            # Skip empty files
            if not text_content.strip():
                log_verbose(f"Skipping empty file: {file_path.name}", level="warning")
                continue
            
            # Split text into chunks
            file_chunks_text = split_text_into_chunks(text_content, chunk_size, overlap)
            
            # Create chunks with metadata (no embeddings)
            file_chunks = []
            for i, chunk_text in enumerate(file_chunks_text):
                chunk_data = {
                    "source_file": file_path.name,
                    "chunk_id": f"{file_path.stem}_chunk_{i}",
                    "chunk_index": i,
                    "text": chunk_text,
                    "character_count": len(chunk_text),
                    "word_count": len(chunk_text.split())
                    # No embedding field for speed
                }
                file_chunks.append(chunk_data)
            
            log_verbose(f"Created {len(file_chunks)} chunks from {file_path.name}", level="success")
            
            # Save each file's chunks to its own JSON
            output_filename = f"{file_path.stem}_chunks_only.json"
            output_file_path = output_path / output_filename
            
            with open(output_file_path, "w", encoding="utf-8") as f:
                json.dump(file_chunks, f, indent=2, ensure_ascii=False)
            
            total_chunks_processed += len(file_chunks)
            log_verbose(f"Saved {len(file_chunks)} text chunks to: {output_filename}", level="success")
            all_processed_files.append(output_file_path)
            
        except Exception as e:
            log_verbose(f"Error processing {file_path.name}: {str(e)}", level="error")
            continue
    
    total_time = time.time() - start_time
    log_verbose(f"\n🎉 LIGHTNING FAST! Processed {len(all_processed_files)} files!")
    log_verbose(f"Total chunks processed: {total_chunks_processed}")
    log_verbose(f"Total processing time: {total_time:.2f} seconds")
    log_verbose(f"Average speed: {total_chunks_processed/total_time:.1f} chunks/second")
    log_verbose("🏃‍♂️ Text-only chunking complete!")
    
    return all_processed_files

# Backwards compatibility function
def vectorize_chunks(input_file="chunked_texts.json", output_file="vectorized_chunks.json", model_name="all-MiniLM-L6-v2"):
    """Legacy function for backwards compatibility - redirects to new text file processing"""
    log_verbose("Note: This function is deprecated. Use process_text_files_and_vectorize() instead.", level="warning")
    log_verbose("Redirecting to process text files directly...", level="process")
    # Extract directory from output_file for the new function
    output_dir = Path(output_file).parent / "vectorized_chunks"
    # Determine embedding type based on model name
    embedding_type = "sentence_transformer" if "MiniLM" in model_name or "sentence" in model_name.lower() else "ollama"
    return process_text_files_and_vectorize(output_dir=str(output_dir), embedding_type=embedding_type, model_name=model_name)

def get_embedding_batch(texts, embedding_type=None, model_name=None, max_workers=4):
    """Universal embedding function that supports both Ollama and SentenceTransformer 🌟"""
    if embedding_type is None:
        embedding_type = EMBEDDING_TYPE
    
    if embedding_type.lower() == "sentence_transformer":
        if model_name is None:
            model_name = SENTENCE_TRANSFORMER_MODEL
        return get_sentence_transformer_embedding_batch(texts, model_name)
    else:  # Default to ollama
        if model_name is None:
            model_name = OLLAMA_MODEL_NAME
        return get_ollama_embedding_batch(texts, model_name, OLLAMA_URL, max_workers)

def get_embedding(text, embedding_type=None, model_name=None):
    """Universal single embedding function that supports both Ollama and SentenceTransformer 🌟"""
    if embedding_type is None:
        embedding_type = EMBEDDING_TYPE
    
    if embedding_type.lower() == "sentence_transformer":
        if model_name is None:
            model_name = SENTENCE_TRANSFORMER_MODEL
        return get_sentence_transformer_embedding(text, model_name)
    else:  # Default to ollama
        if model_name is None:
            model_name = OLLAMA_MODEL_NAME
        return get_ollama_embedding(text, model_name, OLLAMA_URL)

if __name__ == "__main__":
    print("✨ Welcome to the SUPER FAST Text Processor & Vectorizer! ✨")
    print(f"\n🧠 Current embedding configuration:")
    print(f"   Type: {EMBEDDING_TYPE.upper()}")
    if EMBEDDING_TYPE.lower() == "ollama":
        print(f"   Model: {OLLAMA_MODEL_NAME}")
        print(f"   URL: {OLLAMA_URL}")
    else:
        print(f"   Model: {SENTENCE_TRANSFORMER_MODEL}")
        print(f"   Models Folder: {MODELS_FOLDER_PATH}")
    
    print("\n🚀 Choose your processing mode:")
    print("1. Fast text chunking only (no embeddings) - LIGHTNING FAST! ⚡")
    print("2. Full vectorization with current config - Much faster than before! 🚀")
    print("3. Full vectorization with Ollama (override config) 🤖")
    print("4. Full vectorization with SentenceTransformer (override config) 🧠")
    
    choice = input("\nEnter your choice (1-4), or press Enter for default fast mode: ").strip()
    
    if choice == "2":
        print(f"\n🚀 Running full vectorization with {EMBEDDING_TYPE.upper()}...")
        process_text_files_and_vectorize()
    elif choice == "3":
        print("\n🤖 Running full vectorization with Ollama...")
        process_text_files_and_vectorize(embedding_type="ollama", model_name=OLLAMA_MODEL_NAME)
    elif choice == "4":
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            print("❌ SentenceTransformers not available! Install with: pip install sentence-transformers")
        else:
            print("\n🧠 Running full vectorization with SentenceTransformer...")
            process_text_files_and_vectorize(embedding_type="sentence_transformer", model_name=SENTENCE_TRANSFORMER_MODEL)
    else:
        print("\n⚡ Running lightning-fast text chunking only...")
        process_text_files_only()
    
    print("👋 Thanks for processing with us today! Hope it was MUCH faster! 🎉")
