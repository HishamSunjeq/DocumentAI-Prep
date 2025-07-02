import os
import json
from pathlib import Path
from datetime import datetime

def log_verbose(message, level="info", verbose=False):
    """Log message only if verbose mode is enabled"""
    if not verbose and level != "error":
        return
        
    prefix = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "debug": "🔍",
        "process": "⚙️"
    }.get(level, "ℹ️")
    
    print(f"{prefix} {message}")

def clean_json_files(input_folder, output_folder, verbose=False):
    # Check if verbose mode is enabled via environment variable
    if os.getenv('VERBOSE_OUTPUT', 'false').lower() == 'true':
        verbose = True
    
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    
    log_verbose(f"Starting JSON cleaning process", "info", verbose)
    log_verbose(f"Input folder: {input_path}", "info", verbose)
    log_verbose(f"Output folder: {output_path}", "info", verbose)
    
    start_time = datetime.now()
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    json_files = list(input_path.glob("*.json"))
    
    if not json_files:
        log_verbose(f"No JSON files found in {input_folder}", "warning", verbose)
        return
    
    log_verbose(f"Found {len(json_files)} JSON files to process", "info", verbose)
    
    processed_count = 0
    qa_pairs_count = 0

    processed_count = 0
    qa_pairs_count = 0
    
    for file in json_files:
        log_verbose(f"Processing file: {file.name}", "process", verbose)
        
        try:
            with open(file, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    log_verbose(f"Loaded {len(data)} records from {file.name}", "debug", verbose)
                except json.JSONDecodeError as e:
                    log_verbose(f"Skipping {file.name}: JSON decode error - {e}", "error", verbose)
                    continue

            # Extract only prompt and response
            cleaned_data = [
                {"prompt": item["prompt"], "response": item["response"]}
                for item in data if "prompt" in item and "response" in item
            ]
            
            # Count how many items were removed
            removed_count = len(data) - len(cleaned_data)
            if removed_count > 0:
                log_verbose(f"Removed {removed_count} invalid records from {file.name}", "warning", verbose)

            # Save to output folder with same filename
            output_file = output_path / file.name
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

            qa_pairs_count += len(cleaned_data)
            processed_count += 1
            log_verbose(f"Processed: {file.name} - Saved {len(cleaned_data)} clean QA pairs", "success", verbose)
            
        except Exception as e:
            log_verbose(f"Error processing {file.name}: {e}", "error", verbose)
    
    elapsed_time = (datetime.now() - start_time).total_seconds()
    log_verbose(f"JSON cleaning complete in {elapsed_time:.2f} seconds", "success", verbose)
    log_verbose(f"Processed {processed_count} files with {qa_pairs_count} total QA pairs", "success", verbose)

if __name__ == "__main__":
    import sys
    
    # Default paths
    input_folder = "output/qa_pairs"
    output_folder = "output/cleaned_json_output"
    
    # Override with command line arguments if provided
    if len(sys.argv) > 1:
        input_folder = sys.argv[1]
    if len(sys.argv) > 2:
        output_folder = sys.argv[2]
    
    # Always use verbose mode when run directly
    clean_json_files(input_folder, output_folder, verbose=True)