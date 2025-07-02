#!/usr/bin/env python3
"""
Test script to specifically test Ollama connection and GPU/CPU detection
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path so we can import generate_qa
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from generate_qa import QAGenerator

def main():
    """Test Ollama connection with GPU/CPU detection"""
    print("🧪 Ollama Connection and Hardware Test")
    print("=" * 50)
    
    try:
        # Create QA Generator instance (this will test GPU detection)
        print("🔧 Initializing QA Generator...")
        generator = QAGenerator()
        
        print("\n🔍 Testing Ollama connection...")
        # Test the connection (this will test both GPU and CPU fallback if needed)
        connection_success = generator.test_ollama_connection()
        
        if connection_success:
            print("\n✅ Test completed successfully!")
            print(f"   🔧 Final hardware configuration: {'GPU' if generator.use_gpu else 'CPU'}")
            
            # Additional quick test
            print("\n🔄 Performing quick generation test...")
            try:
                test_response = generator.ollama.chat(
                    model=generator.ollama_model,
                    messages=[{"role": "user", "content": "Generate one question about AI and its answer in JSON format."}],
                    options={
                        "num_gpu": -1 if generator.use_gpu else 0,
                        "num_predict": 200,
                        "temperature": 0.7
                    }
                )
                print(f"   ✅ Quick test successful!")
                print(f"   📝 Response: {test_response['message']['content'][:100]}...")
                
            except Exception as e:
                print(f"   ⚠️ Quick test failed: {e}")
                
        else:
            print("\n❌ Test failed!")
            print("   Please check:")
            print("   - Ollama is running (ollama serve)")
            print("   - The specified model is available (ollama list)")
            print("   - Network connectivity to Ollama host")
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("   Please check your configuration and try again")

if __name__ == "__main__":
    main()
