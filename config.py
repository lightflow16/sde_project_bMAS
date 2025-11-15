"""
Configuration file for LbMAS system.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration
# Ollama models (local)
OLLAMA_MODELS = {
    "gpt-oss": "gpt-oss:20b",
    "gemma3": "gemma3:4b",
    "cogito": "cogito:14b",
    "llama3.1": "llama3.1:8b"
}

# API models (remote)
API_MODELS = {
    "llama": "meta-llama/Llama-3.1-70B-Instruct",
    "qwen": "Qwen/Qwen2.5-72B-Instruct"
}

# Use Ollama by default if available, otherwise use API models
USE_OLLAMA = os.getenv("USE_OLLAMA", "true").lower() == "true"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Select which model set to use
LLM_MODELS = OLLAMA_MODELS if USE_OLLAMA else API_MODELS

TEMPERATURE = 0.7
MAX_ROUNDS = 4

# API Configuration (for fallback or when USE_OLLAMA=false)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")

# Dataset paths
DATASET_DIR = "bMAS/datasets"

# Output paths
OUTPUT_DIR = "bMAS/outputs"
RESULTS_DIR = "bMAS/results"

