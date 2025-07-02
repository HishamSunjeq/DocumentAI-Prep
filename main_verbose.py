# Enhanced verbose version of main.py for detailed output
from inspection_agent import process_data_folder
from OCR_Extractor import process_folder_with_ocr
from split_text_chunks import process_text_files_and_vectorize
from generate_qa import QAGenerator
from remove_metadata_fromjson import clean_json_files

import subprocess
import os
import sys
import time
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set verbose mode for detailed output
os.environ['VERBOSE_OUTPUT'] = 'true'

def print_section(title):
    """Print a section header for better visibility"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def print_status(message, status="info"):
    """Print a status message with color coding"""
    prefix = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "start": "🚀",
        "end": "🏁"
    }.get(status, "ℹ️")
    
    print(f"{prefix} {message}")

def check_gpu_status():
    """Check if GPU is available and Ollama is using it (with multi-GPU support)"""
    print_status("Checking GPU status for Ollama...", "start")
    
    # Get selected GPU from environment
    gpu_device_id = os.getenv("GPU_DEVICE_ID", "0")
    
    try:
        # Check if nvidia-smi is available
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode != 0:
            print_status("NVIDIA GPU not detected or drivers not installed", "warning")
            print_status("Ollama will use CPU (slower performance)", "warning")
            return False
        
        print_status(f"Using GPU {gpu_device_id}", "info")
        
        # Check specific GPU memory usage
        result = subprocess.run([
            'nvidia-smi', 
            f'--id={gpu_device_id}',
            '--query-gpu=name,memory.used,memory.total', 
            '--format=csv,noheader,nounits'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            gpu_info = result.stdout.strip().split(', ')
            if len(gpu_info) >= 3:
                gpu_name = gpu_info[0]
                used_mb = int(gpu_info[1])
                total_mb = int(gpu_info[2])
                print_status(f"GPU {gpu_device_id}: {gpu_name}", "info")
                print_status(f"Memory: {used_mb}MB / {total_mb}MB used", "info")
                
                if used_mb < 100:  # Very low usage might indicate CPU mode
                    print_status("Low GPU memory usage - Ollama might be using CPU", "warning")
            return True
    except Exception as e:
        print_status(f"Error checking GPU: {e}", "error")
    return False

def check_folders():
    """Ensure all required folders exist"""
    print_status("Checking and creating required folders...", "start")
    
    # Get folder paths from environment or use defaults
    data_folder = os.getenv("DATA_FOLDER_PATH", "data")
    output_folder = os.getenv("OUTPUT_FOLDER_PATH", "output")
    ocr_output_folder = os.getenv("OCR_OUTPUT_FOLDER_PATH", "output/ocr_output")
    
    # Create Path objects
    data_path = Path(data_folder)
    output_path = Path(output_folder)
    ocr_output_path = Path(ocr_output_folder)
    qa_output_path = Path(output_folder) / "qa_pairs"
    cleaned_json_path = Path(output_folder) / "cleaned_json_output"
    chunked_output_path = Path(output_folder) / "chunked_output"
    
    # Check and create directories
    folders = {
        "Data folder": data_path,
        "Output folder": output_path,
        "OCR output folder": ocr_output_path,
        "QA pairs folder": qa_output_path,
        "Cleaned JSON folder": cleaned_json_path,
        "Chunked output folder": chunked_output_path
    }
    
    for name, folder in folders.items():
        if not folder.exists():
            print_status(f"Creating {name}: {folder}", "info")
            folder.mkdir(parents=True, exist_ok=True)
        else:
            print_status(f"{name} exists at: {folder}", "success")
    
    # Check if data folder has files
    if data_path.exists():
        files = list(data_path.glob("*"))
        print_status(f"Data folder contains {len(files)} files/folders", "info")
        
        # List some of the files
        if files:
            print_status("Sample files:", "info")
            for file in files[:5]:  # Show first 5 files
                print(f"   - {file.name}")
            if len(files) > 5:
                print(f"   - ... and {len(files) - 5} more")
    
    return True

def step1_inspection_agent():
    """Run the inspection agent to analyze files in the data folder"""
    print_section("STEP 1: INSPECTION AGENT")
    print_status("Starting file inspection process...", "start")
    
    # Ensure folders exist
    check_folders()
    
    # Get folder paths from environment or use defaults
    data_folder = os.getenv("DATA_FOLDER_PATH", "data")
    output_folder = os.getenv("OUTPUT_FOLDER_PATH", "output")
    
    print_status(f"Analyzing files in: {data_folder}", "info")
    print_status(f"Results will be saved to: {output_folder}", "info")
    
    # Start timer
    start_time = time.time()
    
    # Process the data folder
    try:
        results = process_data_folder(data_folder, output_folder)
        valid_files = sum(1 for file in results if file.get("is_valid", False))
        
        # Print results
        print_status(f"Inspection completed in {time.time() - start_time:.2f} seconds", "success")
        print_status(f"Processed {len(results)} files, {valid_files} are valid for extraction", "success")
        
        # Show details of issues if any
        invalid_files = [file for file in results if not file.get("is_valid", False)]
        if invalid_files:
            print_status(f"Found {len(invalid_files)} files with issues:", "warning")
            for file in invalid_files:
                notes = file.get("notes", "Unknown issue")
                print(f"   - {file['filename']}: {notes}")
        
        return True
    except Exception as e:
        print_status(f"Error during inspection: {e}", "error")
        return False

def step2_ocr():
    """Run OCR processing on files in the data folder"""
    print_section("STEP 2: OCR PROCESSING")
    print_status("Starting OCR text extraction...", "start")
    
    # Get folder paths from environment or use defaults
    data_folder = os.getenv("DATA_FOLDER_PATH", "data")
    ocr_output_folder = os.getenv("OCR_OUTPUT_FOLDER_PATH", "output/ocr_output")
    
    print_status(f"Processing files from: {data_folder}", "info")
    print_status(f"Extracted text will be saved to: {ocr_output_folder}", "info")
    
    # Start timer
    start_time = time.time()
    
    # Make sure environment is set for maximum verbosity
    os.environ['VERBOSE_OUTPUT'] = 'true'
    os.environ['DEBUG'] = 'true'
    
    # Process the data folder with OCR
    try:
        print_status("Running OCR on each file (this may take some time)...", "info")
        print_status("You will see detailed progress for each file being processed", "info")
        
        results = process_folder_with_ocr(data_folder, ocr_output_folder)
        
        # Print results
        print_status(f"OCR processing completed in {time.time() - start_time:.2f} seconds", "success")
        print_status(f"Processed {len(results)} files", "success")
        
        # Calculate statistics
        successful = sum(1 for result in results if result.get("success", False))
        word_count = sum(result.get("word_count", 0) for result in results)
        
        print_status(f"Successfully extracted text from {successful} files", "success")
        print_status(f"Total word count: {word_count:,}", "info")
        
        # Show details of all processed files
        print_status("File processing summary:", "info")
        for result in results:
            status = "✅" if result.get("success", False) else "❌"
            filename = Path(result.get("input_file", "unknown")).name
            word_count = result.get("word_count", 0)
            print(f"   {status} {filename}: {word_count:,} words")
        
        # Show details of failures if any
        failures = [result for result in results if not result.get("success", False)]
        if failures:
            print_status(f"Failed to extract text from {len(failures)} files:", "warning")
            for failure in failures:
                print(f"   - {failure['input_file']}: {failure.get('error', 'Unknown error')}")
        
        return True
    except Exception as e:
        print_status(f"Error during OCR processing: {e}", "error")
        return False

def step4_qa_generation():
    """Generate QA pairs from processed text chunks"""
    print_section("STEP 4: QA GENERATION")
    print_status("Starting QA pair generation...", "start")
    
    # Make sure environment is set for maximum verbosity
    os.environ['VERBOSE_OUTPUT'] = 'true'
    os.environ['DEBUG'] = 'true'
    
    # Check GPU status
    gpu_available = check_gpu_status()
    print_status(f"Using {'GPU' if gpu_available else 'CPU'} for generation", "info")
    
    # Start timer
    start_time = time.time()
    
    try:
        print_status("This step uses an AI model to generate questions and answers from the text", "info")
        print_status("You will see detailed progress as each text chunk is processed", "info")
        
        # Initialize QA generator
        generator = QAGenerator()
        
        # Print configuration details
        print_status(f"Configuration:", "info")
        print_status(f"  Input folder: {generator.input_folder}", "info")
        print_status(f"  Output folder: {generator.output_folder}", "info")
        print_status(f"  Ollama host: {generator.ollama_host}", "info")
        print_status(f"  Ollama model: {generator.ollama_model}", "info")
        print_status(f"  Q&A pairs per chunk: {generator.qa_pairs_per_chunk}", "info")
        
        # Run the generation process
        generator.process_all_files()
        
        # Print results
        print_status(f"QA generation completed in {time.time() - start_time:.2f} seconds", "success")
        print_status(f"Used model: {generator.ollama_model}", "info")
        
        # Try to get some statistics from the output folder
        try:
            output_path = Path(generator.output_folder)
            json_files = list(output_path.glob("*.json"))
            total_qa_pairs = 0
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        total_qa_pairs += len(data)
                except Exception:
                    pass
            
            print_status(f"Generated {len(json_files)} output files with {total_qa_pairs} QA pairs", "success")
        except Exception as e:
            print_status(f"Could not gather output statistics: {e}", "warning")
        
        return True
    except Exception as e:
        print_status(f"Error during QA generation: {e}", "error")
        return False

if __name__ == "__main__":
    # For direct testing
    command = sys.argv[1] if len(sys.argv) > 1 else None
    
    if command == "step1":
        step1_inspection_agent()
    elif command == "step2":
        step2_ocr()
    elif command == "step4":
        step4_qa_generation()
    else:
        print("Please specify which step to run: step1, step2, or step4")
