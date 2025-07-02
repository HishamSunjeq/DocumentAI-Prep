#!/usr/bin/env python3
"""
Ollama GPU Setup and Diagnostic Tool
Helps diagnose and fix Ollama GPU usage issues with multi-GPU support
"""
import subprocess
import json
import sys
import os
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_gpu_info():
    """Get detailed information about all available GPUs"""
    try:
        result = subprocess.run([
            'nvidia-smi', 
            '--query-gpu=index,name,memory.total,memory.used,utilization.gpu,power.draw,power.limit', 
            '--format=csv,noheader,nounits'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            gpus = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 7:
                        gpus.append({
                            'index': int(parts[0]),
                            'name': parts[1],
                            'memory_total': int(parts[2]),
                            'memory_used': int(parts[3]),
                            'utilization': int(parts[4]),
                            'power_draw': float(parts[5]) if parts[5] != '[N/A]' else 0,
                            'power_limit': float(parts[6]) if parts[6] != '[N/A]' else 0
                        })
            return gpus
    except Exception as e:
        print(f"   ⚠️ Error getting GPU info: {e}")
    return []

def auto_select_best_gpu():
    """Automatically select the most powerful GPU"""
    gpus = get_gpu_info()
    if not gpus:
        return 0
    
    # Score GPUs based on memory and power limit
    best_gpu = max(gpus, key=lambda gpu: (gpu['memory_total'], gpu['power_limit']))
    return best_gpu['index']

def display_gpu_options():
    """Display available GPUs and let user choose"""
    gpus = get_gpu_info()
    if not gpus:
        print("   ❌ No GPUs detected")
        return 0
    
    print("\n🎮 Available GPUs:")
    for gpu in gpus:
        memory_pct = (gpu['memory_used'] / gpu['memory_total']) * 100 if gpu['memory_total'] > 0 else 0
        print(f"   GPU {gpu['index']}: {gpu['name']}")
        print(f"      Memory: {gpu['memory_used']}MB / {gpu['memory_total']}MB ({memory_pct:.1f}% used)")
        print(f"      Power: {gpu['power_draw']:.1f}W / {gpu['power_limit']:.1f}W")
        print(f"      Utilization: {gpu['utilization']}%")
        print()
    
    # Check environment variable first
    env_gpu = os.getenv("GPU_DEVICE_ID")
    if env_gpu:
        try:
            selected_gpu = int(env_gpu)
            if 0 <= selected_gpu < len(gpus):
                print(f"   🔧 Using GPU {selected_gpu} from environment variable")
                return selected_gpu
        except ValueError:
            pass
    
    # Auto-select if enabled
    if os.getenv("GPU_AUTO_SELECT", "false").lower() == "true":
        best_gpu = auto_select_best_gpu()
        print(f"   🤖 Auto-selected GPU {best_gpu} (most powerful)")
        return best_gpu
    
    # Ask user to choose
    while True:
        try:
            choice = input(f"   Select GPU (0-{len(gpus)-1}) or press Enter for GPU 0: ").strip()
            if not choice:
                return 0
            gpu_id = int(choice)
            if 0 <= gpu_id < len(gpus):
                return gpu_id
            else:
                print(f"   ❌ Invalid choice. Please select 0-{len(gpus)-1}")
        except ValueError:
            print("   ❌ Please enter a valid number")

def check_gpu_availability():
    """Check if GPU is available and working"""
    print("🔍 Checking GPU Availability...")
    
    try:
        # Check NVIDIA GPU
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ NVIDIA GPU detected")
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Driver Version' in line:
                    print(f"   📊 {line.strip()}")
                if '|' in line and 'MiB' in line and not line.startswith('+'):
                    print(f"   💾 {line.strip()}")
            return True
        else:
            print("   ❌ NVIDIA GPU not detected or nvidia-smi not available")
            return False
    except FileNotFoundError:
        print("   ❌ nvidia-smi not found. Make sure NVIDIA drivers are installed.")
        return False

def check_ollama_status():
    """Check Ollama service status"""
    print("\n🔍 Checking Ollama Status...")
    
    try:
        # Check if Ollama is running
        result = subprocess.run(['ollama', 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Ollama is running")
            print(f"   📊 Active models:\n{result.stdout}")
            return True
        else:
            print("   ❌ Ollama not running or not accessible")
            return False
    except FileNotFoundError:
        print("   ❌ Ollama command not found. Make sure Ollama is installed.")
        return False

def check_model_gpu_usage(model_name="mistral"):
    """Check if a specific model is using GPU"""
    print(f"\n🔍 Checking GPU usage for model: {model_name}")
    
    try:
        # Test model with GPU monitoring
        print("   📊 Testing model inference with GPU monitoring...")
        
        # Start GPU monitoring
        gpu_before = get_gpu_stats()
        if gpu_before:
            print(f"   💾 GPU Memory before: {gpu_before}")
        
        # Test inference
        result = subprocess.run([
            'ollama', 'run', model_name, 
            '--verbose',
            'Hello, this is a test. Respond briefly.'
        ], capture_output=True, text=True, timeout=30)
        
        # Check GPU after
        gpu_after = get_gpu_stats()
        if gpu_after:
            print(f"   💾 GPU Memory after: {gpu_after}")
            
            # Compare memory usage
            if gpu_after['memory_used'] > gpu_before['memory_used']:
                print("   ✅ Model is using GPU!")
                return True
            else:
                print("   ❌ Model appears to be using CPU")
                return False
        else:
            print("   ⚠️ Cannot determine GPU usage")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ⚠️ Model test timed out")
        return False
    except Exception as e:
        print(f"   ❌ Error testing model: {e}")
        return False

def get_gpu_stats():
    """Get current GPU memory usage"""
    try:
        result = subprocess.run([
            'nvidia-smi', 
            '--query-gpu=memory.used,memory.total,utilization.gpu', 
            '--format=csv,noheader,nounits'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            line = result.stdout.strip().split('\n')[0]
            parts = line.split(', ')
            return {
                'memory_used': int(parts[0]),
                'memory_total': int(parts[1]),
                'utilization': int(parts[2])
            }
    except:
        pass
    return None

def update_env_file_gpu(gpu_id):
    """Update .env file with selected GPU ID"""
    env_file = Path(".env")
    if not env_file.exists():
        return
    
    try:
        # Read current .env file
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Update GPU settings
        updated_lines = []
        gpu_device_updated = False
        cuda_visible_updated = False
        
        for line in lines:
            if line.startswith('GPU_DEVICE_ID='):
                updated_lines.append(f'GPU_DEVICE_ID={gpu_id}\n')
                gpu_device_updated = True
            elif line.startswith('CUDA_VISIBLE_DEVICES='):
                updated_lines.append(f'CUDA_VISIBLE_DEVICES={gpu_id}\n')
                cuda_visible_updated = True
            else:
                updated_lines.append(line)
        
        # Add missing GPU settings if not found
        if not gpu_device_updated:
            updated_lines.append(f'GPU_DEVICE_ID={gpu_id}\n')
        if not cuda_visible_updated:
            updated_lines.append(f'CUDA_VISIBLE_DEVICES={gpu_id}\n')
        
        # Write back to .env file
        with open(env_file, 'w') as f:
            f.writelines(updated_lines)
        
        print(f"   📝 Updated .env file with GPU {gpu_id}")
        
    except Exception as e:
        print(f"   ⚠️ Could not update .env file: {e}")

def fix_ollama_gpu(selected_gpu_id=None):
    """Attempt to fix Ollama GPU issues with specific GPU selection"""
    print("\n🔧 Attempting to fix Ollama GPU usage...")
    
    # Select GPU if not specified
    if selected_gpu_id is None:
        selected_gpu_id = display_gpu_options()
    
    print(f"   🎯 Using GPU {selected_gpu_id}")
    
    # Step 1: Stop Ollama
    print("   1. Stopping Ollama service...")
    try:
        subprocess.run(['ollama', 'stop'], capture_output=True)
        time.sleep(2)
    except:
        pass
    
    # Step 2: Set GPU environment variables with selected GPU
    print("   2. Setting GPU environment variables...")
    
    # Set CUDA environment variables with selected GPU
    gpu_env = {
        'CUDA_VISIBLE_DEVICES': str(selected_gpu_id),
        'GPU_DEVICE_ID': str(selected_gpu_id),
        'OLLAMA_HOST': '127.0.0.1:11434',
        'OLLAMA_NUM_PARALLEL': '1',
        'OLLAMA_MAX_LOADED_MODELS': '1',
        'OLLAMA_GPU_OVERHEAD': '0',
    }
    
    # Update environment
    for key, value in gpu_env.items():
        os.environ[key] = value
        print(f"      {key}={value}")
    
    # Update .env file with selected GPU
    update_env_file_gpu(selected_gpu_id)
    
    # Step 3: Start Ollama with GPU
    print("   3. Starting Ollama with GPU optimization...")
    try:
        # Start Ollama serve in background
        subprocess.Popen(['ollama', 'serve'], 
                        env={**os.environ, **gpu_env},
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        time.sleep(5)
        print("   ✅ Ollama restarted with GPU settings")
    except Exception as e:
        print(f"   ❌ Failed to restart Ollama: {e}")
        return False
    
    return True

def pull_gpu_optimized_model(model_name="mistral"):
    """Pull model with GPU optimization"""
    print(f"\n📥 Pulling {model_name} with GPU optimization...")
    
    try:
        # Pull the model
        result = subprocess.run(['ollama', 'pull', model_name], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ {model_name} pulled successfully")
            return True
        else:
            print(f"   ❌ Failed to pull {model_name}: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Error pulling model: {e}")
        return False

def create_gpu_optimized_env():
    """Create optimized .env file for GPU usage"""
    print("\n📝 Creating GPU-optimized .env settings...")
    
    env_additions = """
# GPU Optimization Settings for Ollama
OLLAMA_HOST=127.0.0.1:11434
OLLAMA_NUM_PARALLEL=1
OLLAMA_MAX_LOADED_MODELS=1
OLLAMA_GPU_OVERHEAD=0
CUDA_VISIBLE_DEVICES=0

# QA Generation GPU Settings
QA_OLLAMA_HOST=http://127.0.0.1:11434
QA_OPTIMIZE_OLLAMA=true
QA_BATCH_SIZE=3
QA_ENABLE_MONITORING=true
"""
    
    # Read current .env
    env_file = Path(".env")
    current_content = ""
    if env_file.exists():
        current_content = env_file.read_text()
    
    # Append GPU settings if not present
    if "OLLAMA_GPU_OVERHEAD" not in current_content:
        with open(env_file, "a") as f:
            f.write(env_additions)
        print("   ✅ GPU settings added to .env file")
    else:
        print("   ℹ️ GPU settings already present in .env file")

def test_qa_generation_gpu():
    """Test QA generation with GPU monitoring"""
    print("\n🧪 Testing QA Generation with GPU monitoring...")
    
    try:
        from generate_qa import QAGenerator
        
        # Set monitoring to true for this test
        os.environ["QA_ENABLE_MONITORING"] = "true"
        os.environ["QA_BATCH_SIZE"] = "1"
        
        generator = QAGenerator()
        
        # Test connection with GPU monitoring
        print("   🔄 Testing Ollama connection...")
        success = generator.test_ollama_connection()
        
        if success:
            print("   ✅ QA generation test successful with GPU monitoring")
        else:
            print("   ❌ QA generation test failed")
            
        return success
        
    except Exception as e:
        print(f"   ❌ QA generation test error: {e}")
        return False

def auto_fix_gpu(verbose=True):
    """Automatic GPU fix function that can be called programmatically"""
    if verbose:
        print("🔧 Starting automatic GPU optimization...")
    
    # Step 1: Check GPU availability
    gpu_available = check_gpu_availability()
    if not gpu_available:
        if verbose:
            print("❌ No GPU detected - cannot apply GPU fixes")
        return False
    
    # Step 2: Apply GPU fixes
    try:
        # Get GPU selection (use environment or auto-select)
        gpu_device_id = os.getenv("GPU_DEVICE_ID")
        if not gpu_device_id:
            if os.getenv("GPU_AUTO_SELECT", "false").lower() == "true":
                gpu_device_id = auto_select_best_gpu()
            else:
                gpu_device_id = 0  # Default to GPU 0
        
        # Apply fix
        success = fix_ollama_gpu(int(gpu_device_id))
        if not success:
            if verbose:
                print("❌ GPU fix failed")
            return False
        
        # Wait for Ollama to restart
        time.sleep(3)
        
        # Verify fix worked
        model_using_gpu = check_model_gpu_usage()
        if model_using_gpu:
            if verbose:
                print("✅ GPU optimization successful!")
            return True
        else:
            if verbose:
                print("⚠️ GPU fix applied but model still not using GPU")
            return False
            
    except Exception as e:
        if verbose:
            print(f"❌ Auto-fix error: {e}")
        return False

def main():
    """Main diagnostic and fix function"""
    print("🚀 Ollama GPU Diagnostic and Fix Tool")
    print("=" * 50)
    
    # Step 1: Check GPU
    gpu_available = check_gpu_availability()
    if not gpu_available:
        print("\n❌ No GPU detected. Ollama will use CPU.")
        print("💡 Install NVIDIA drivers and CUDA toolkit for GPU support.")
        return
    
    # Step 2: Check Ollama
    ollama_running = check_ollama_status()
    if not ollama_running:
        print("\n⚠️ Ollama not running. Starting fix process...")
        fix_ollama_gpu()
        time.sleep(3)
        ollama_running = check_ollama_status()
    
    if not ollama_running:
        print("\n❌ Could not start Ollama. Please check installation.")
        return
    
    # Step 3: Check model GPU usage
    model_using_gpu = check_model_gpu_usage()
    
    if not model_using_gpu:
        print("\n🔧 Model not using GPU. Applying fixes...")
        
        # Apply fixes
        fix_ollama_gpu()
        create_gpu_optimized_env()
        
        # Wait and test again
        time.sleep(5)
        model_using_gpu = check_model_gpu_usage()
        
        if model_using_gpu:
            print("\n✅ GPU fix successful!")
        else:
            print("\n❌ GPU fix unsuccessful. Manual intervention needed.")
            print("\n💡 Manual steps to try:")
            print("   1. Restart your computer")
            print("   2. Run: ollama stop && ollama serve")
            print("   3. Set CUDA_VISIBLE_DEVICES=0")
            print("   4. Check GPU memory: nvidia-smi")
    
    # Step 4: Test QA generation
    if model_using_gpu:
        test_qa_generation_gpu()
    
    print("\n📊 Final Status:")
    print(f"   GPU Available: {'✅' if gpu_available else '❌'}")
    print(f"   Ollama Running: {'✅' if ollama_running else '❌'}")
    print(f"   Model Using GPU: {'✅' if model_using_gpu else '❌'}")
    
    if gpu_available and ollama_running and model_using_gpu:
        print("\n🎉 All systems ready for fast GPU-accelerated QA generation!")
    else:
        print("\n⚠️ Some issues detected. Check the steps above.")

if __name__ == "__main__":
    main()
