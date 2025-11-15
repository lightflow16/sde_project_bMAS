"""
Test script to verify Ollama connectivity and model availability.
"""
import requests
import os
import sys

# Add parent directories to path for imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
_bmas_dir = os.path.dirname(_current_dir)
_root_dir = os.path.dirname(_bmas_dir)
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)
if _bmas_dir not in sys.path:
    sys.path.insert(0, _bmas_dir)

import config
from llm_integration.api import call_llm, get_available_models


def test_ollama_connection():
    """Test if Ollama is running and accessible."""
    try:
        response = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"[OK] Ollama is running at {config.OLLAMA_BASE_URL}")
            print(f"   Found {len(models)} models:")
            for model in models:
                print(f"   - {model.get('name', 'unknown')}")
            return True
        else:
            print(f"[ERROR] Ollama responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot connect to Ollama at {config.OLLAMA_BASE_URL}")
        print("   Make sure Ollama is running: ollama serve")
        return False
    except Exception as e:
        print(f"[ERROR] Error testing Ollama: {e}")
        return False


def test_model_call():
    """Test a simple model call."""
    print("\n" + "="*60)
    print("Testing Model Call")
    print("="*60)
    
    available_models = get_available_models()
    print(f"Available models in config: {available_models}")
    
    if not available_models:
        print("[ERROR] No models configured!")
        return False
    
    # Use the first available model
    test_model = available_models[0]
    print(f"\nTesting with model: {test_model}")
    
    test_prompt = "What is 2 + 2? Answer in one sentence."
    
    try:
        print(f"Sending prompt: {test_prompt}")
        result = call_llm(test_prompt, model_name=test_model)
        
        print(f"\n[OK] Model call successful!")
        print(f"Response: {result['content'][:200]}...")
        print(f"Tokens used: {result['metadata'].get('tokens_used', 'N/A')}")
        return True
    except Exception as e:
        print(f"\n[ERROR] Model call failed: {e}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("Ollama Connection Test")
    print("="*60)
    
    if config.USE_OLLAMA:
        print(f"\nUsing Ollama (base URL: {config.OLLAMA_BASE_URL})")
        if test_ollama_connection():
            test_model_call()
        else:
            print("\n[WARNING] Ollama not available. System will fall back to API calls.")
    else:
        print("\n[WARNING] Ollama is disabled. Set USE_OLLAMA=true to enable.")
        print("   Current configuration uses API models.")

