from inspection_agent import process_data_folder
from OCR_Extractor import process_folder_with_ocr
from split_text_chunks import process_text_files_and_vectorize
from generate_qa import QAGenerator
from remove_metadata_fromjson import clean_json_files


import subprocess
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def check_gpu_status():
    """Check if GPU is available and Ollama is using it (with multi-GPU support)"""
    print("🔍 Checking GPU status for Ollama...")
    
    # Get selected GPU from environment
    gpu_device_id = os.getenv("GPU_DEVICE_ID", "0")
    
    try:
        # Check if nvidia-smi is available
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode != 0:
            print("   ⚠️ NVIDIA GPU not detected or drivers not installed")
            print("   💡 Ollama will use CPU (slower performance)")
            return False
        
        print(f"   🎮 Using GPU {gpu_device_id}")
        
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
                print(f"   📊 GPU {gpu_device_id}: {gpu_name}")
                print(f"   📊 Memory: {used_mb}MB / {total_mb}MB used")
                
                if used_mb < 100:  # Very low usage might indicate CPU mode
                    print("   ⚠️ Low GPU memory usage - Ollama might be using CPU")
                    print("   💡 Run 'python fix_ollama_gpu.py' to diagnose and fix")
                    return False
                else:
                    print("   ✅ GPU appears to be in use")
                    return True
        
    except FileNotFoundError:
        print("   ❌ nvidia-smi not found - GPU support not available")
        print("   💡 Install NVIDIA drivers for GPU acceleration")
        return False
    except Exception as e:
        print(f"   ⚠️ Error checking GPU: {e}")
        return False

def step4_qa_generation():
    """Generate QA pairs with GPU optimization and auto-fix"""
    print("Step 4: QA Generation with GPU Optimization")
    
    # Check GPU status first
    gpu_available = check_gpu_status()
    
    if not gpu_available:
        print("   ⚠️ GPU not optimal - attempting automatic fix...")
        
        # Check if auto-fix is enabled
        auto_fix_enabled = os.getenv("GPU_AUTO_FIX", "true").lower() == "true"
        
        if auto_fix_enabled:
            print("   🔧 Auto-fix enabled - running GPU optimization...")
            try:
                # Import and run GPU fix
                from fix_ollama_gpu import auto_fix_gpu
                success = auto_fix_gpu(verbose=True)
                
                if success:
                    print("   ✅ GPU fix completed - rechecking status...")
                    gpu_available = check_gpu_status()
                else:
                    print("   ❌ Auto-fix failed")
            except Exception as e:
                print(f"   ❌ Auto-fix error: {e}")
                print("   💡 Try manual fix: python fix_ollama_gpu.py")
        else:
            # Ask user if they want auto-fix
            user_input = input("   🔧 Attempt automatic GPU fix? (y/n/manual): ").lower()
            
            if user_input == 'y':
                print("   🔧 Running automatic GPU optimization...")
                try:
                    # Import and run GPU fix
                    from fix_ollama_gpu import auto_fix_gpu
                    success = auto_fix_gpu(verbose=True)
                    
                    if success:
                        print("   ✅ GPU fix completed - rechecking status...")
                        gpu_available = check_gpu_status()
                        if not gpu_available:
                            print("   ⚠️ GPU fix didn't resolve the issue")
                    else:
                        print("   ❌ GPU fix failed")
                except Exception as e:
                    print(f"   ❌ Auto-fix error: {e}")
                    print("   💡 Try manual fix: python fix_ollama_gpu.py")
            
            elif user_input == 'manual':
                print("   💡 Run manual fix: python fix_ollama_gpu.py")
                print("   ⏸️ QA generation paused - run the fix and restart")
                return
        
        # If still no GPU, ask about CPU fallback
        if not gpu_available:
            print("   ⚠️ GPU still not available - QA generation will be slower")
            fallback_input = input("   Continue with CPU? (y/n): ").lower()
            if fallback_input != 'y':
                print("   ⏸️ QA generation skipped")
                return
    
    try:
        generator = QAGenerator()
        
        # Test connection first
        if not generator.test_ollama_connection():
            print("   ❌ Cannot connect to Ollama")
            print("   💡 Make sure Ollama is running: ollama serve")
            return
        
        generator.process_all_files()
        print("   ✅ QA generation completed successfully")
        
    except Exception as e:
        print(f"   ❌ QA generation failed: {e}")
        print("   💡 Try running: python fix_ollama_gpu.py")

def step1_inspection_agent():
    """Main function to process data folder using environment variables."""
    
    data_folder = os.getenv("DATA_FOLDER_PATH")
    output_folder = os.getenv("OUTPUT_FOLDER_PATH")
    
    if not data_folder:
        print("ERROR: DATA_FOLDER_PATH not found in .env file")
        exit(1)
    
    print(f"Processing data from: {data_folder}")
    print(f"Output folder: {output_folder or 'Not specified - results will not be saved'}")
    
    # Process the data folder
    results = process_data_folder(data_folder, output_folder)
    print(f"Processed {len(results)} files successfully")

def step2_ocr():
    process_folder_with_ocr(
        data_folder=os.getenv("DATA_FOLDER_PATH"),
        output_folder=os.getenv("OCR_OUTPUT_FOLDER_PATH")
    )


if __name__ == "__main__":
    print("Starting data processing steps...")
    
    # When running the entire pipeline, uncomment these lines:
    step1_inspection_agent()
    
    print("Step 2: OCR Processing")
    step2_ocr()
    print("Step 2: Finished")

    print("Step 3: Text Processing and Vectorization")
    process_text_files_and_vectorize()
    print("Step 3: Finished")
    
    print("Step 4: QA Generation")
    # Use the new GPU-optimized QA generation
    step4_qa_generation()
    print("Step 4: Finished")
    
    print("Step 5: Clean JSON Files")
    # Clean JSON files by removing metadata
    clean_json_files("output/qa_pairs", "output/cleaned_json_output")
    
    print("All steps completed successfully!")
