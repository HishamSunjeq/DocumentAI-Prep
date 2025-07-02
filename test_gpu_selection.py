#!/usr/bin/env python3
"""
Quick GPU Selection Test
Test multi-GPU support without running full QA generation
"""
import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

def list_available_gpus():
    """List all available GPUs"""
    print("🎮 Available GPUs:")
    try:
        result = subprocess.run([
            'nvidia-smi', 
            '--query-gpu=index,name,memory.total,utilization.gpu', 
            '--format=csv,noheader,nounits'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            gpus = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 4:
                        gpu_id = parts[0]
                        name = parts[1]
                        memory = parts[2]
                        util = parts[3]
                        print(f"   GPU {gpu_id}: {name} ({memory}MB, {util}% util)")
                        gpus.append(gpu_id)
            return gpus
    except Exception as e:
        print(f"   ❌ Error listing GPUs: {e}")
    return []

def test_gpu_selection():
    """Test GPU selection from environment"""
    print("\n🔧 Testing GPU Selection:")
    
    # Check current settings
    gpu_device_id = os.getenv("GPU_DEVICE_ID", "0")
    cuda_visible = os.getenv("CUDA_VISIBLE_DEVICES", "0")
    auto_select = os.getenv("GPU_AUTO_SELECT", "false")
    
    print(f"   GPU_DEVICE_ID: {gpu_device_id}")
    print(f"   CUDA_VISIBLE_DEVICES: {cuda_visible}")
    print(f"   GPU_AUTO_SELECT: {auto_select}")
    
    # Test specific GPU
    try:
        result = subprocess.run([
            'nvidia-smi', 
            f'--id={gpu_device_id}',
            '--query-gpu=name,memory.used,memory.total', 
            '--format=csv,noheader,nounits'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            gpu_info = result.stdout.strip().split(', ')
            if len(gpu_info) >= 3:
                name = gpu_info[0]
                used = gpu_info[1]
                total = gpu_info[2]
                print(f"   ✅ Selected GPU {gpu_device_id}: {name}")
                print(f"   📊 Memory: {used}MB / {total}MB used")
            else:
                print(f"   ❌ Could not get info for GPU {gpu_device_id}")
        else:
            print(f"   ❌ GPU {gpu_device_id} not found or accessible")
    except Exception as e:
        print(f"   ❌ Error testing GPU {gpu_device_id}: {e}")

def main():
    print("🚀 GPU Selection Test")
    print("=" * 30)
    
    # List available GPUs
    gpus = list_available_gpus()
    
    if not gpus:
        print("❌ No GPUs detected")
        return
    
    # Test current selection
    test_gpu_selection()
    
    print("\n💡 To change GPU selection:")
    print("   1. Edit .env file: GPU_DEVICE_ID=1")
    print("   2. Run: python fix_ollama_gpu.py")
    print("   3. Restart QA generation")

if __name__ == "__main__":
    main()
