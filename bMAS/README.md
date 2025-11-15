# LbMAS: Blackboard-based LLM Multi-Agent System

Implementation of a blackboard-based LLM multi-agent system (LbMAS) based on the paper "Exploring Advanced LLM Multi-Agent Systems Based on Blackboard Architecture."

## Project Structure

```
bMAS/
├── agents/              # Agent implementations
│   ├── base_agent.py
│   ├── predefined.py    # Planner, Decider, Critic, Cleaner, ConflictResolver
│   └── generated_expert.py
├── blackboard/          # Blackboard shared memory
│   └── blackboard.py
├── control_unit/        # Control unit for agent scheduling
│   └── scheduler.py
├── llm_integration/     # LLM API integration
│   └── api.py
├── prompts/             # Prompt templates
│   └── predefined_prompts.py
├── experiment_runner/   # Experiment execution
│   ├── run_experiment.py
│   └── data_loader.py
├── datasets/            # Dataset storage
├── outputs/             # Experiment outputs
├── config.py            # Configuration
├── main.py              # Main entry point
└── requirements.txt     # Dependencies
```

## Setup

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure LLM backend:**
   
   **Option A: Use Ollama (Local Models - Recommended)**
   - Make sure Ollama is installed and running: `ollama serve`
   - The system will use your local Ollama models by default
   - Test connection: `python test_ollama.py`
   
   **Option B: Use API (Remote Models)**
   - Create a `.env` file in the project root:
     ```
     USE_OLLAMA=false
     OPENAI_API_KEY=your_openai_key
     HUGGINGFACE_API_KEY=your_huggingface_key
     ```

## Usage

### Single Problem Mode

Run a single experiment on a problem:

```bash
python main.py --mode single --problem "What is 2 + 2?"
```

### Batch Mode

Run experiments on a dataset:

```bash
python main.py --mode batch --dataset datasets/sample.json --max-rounds 4
```

### Create Sample Dataset

Create a sample dataset for testing:

```bash
python main.py --mode sample
```

## Features

- **Blackboard Architecture**: Shared memory system with public and private spaces
- **Dynamic Agent Generation**: Expert agents generated based on problem domain
- **Predefined Agents**: Planner, Decider, Critic, Cleaner, ConflictResolver
- **Control Unit**: LLM-based agent scheduling
- **Multi-Round Execution**: Iterative problem-solving with configurable rounds
- **Token Tracking**: Monitor LLM API usage
- **Experiment Runner**: Batch processing with evaluation

## Configuration

Edit `config.py` to adjust:
- **Ollama Models** (default): gpt-oss:20b, gemma3:4b, cogito:14b, llama3.1:8b
- **API Models** (fallback): Llama 3.1-70b, Qwen 2.5-72b
- Temperature settings (default: 0.7)
- Maximum rounds (default: 4)
- Dataset and output directories

### Environment Variables

Create a `.env` file to customize:
```bash
# Use Ollama (true) or API (false)
USE_OLLAMA=true

# Ollama base URL (if different from default)
OLLAMA_BASE_URL=http://localhost:11434

# API keys (only needed if USE_OLLAMA=false)
OPENAI_API_KEY=your_key
HUGGINGFACE_API_KEY=your_key
```

## Testing Ollama Connection

Test your Ollama setup:
```bash
python test_ollama.py
```

This will verify:
- Ollama is running and accessible
- Available models are detected
- A test model call works correctly

## Notes

- **Ollama is enabled by default** - Make sure `ollama serve` is running
- The system automatically falls back to API calls if Ollama is unavailable
- Mock responses are used only if all LLM backends fail (for testing)
- The system is designed to work with JSON-formatted datasets

## License

This implementation is based on the research paper and is for educational/research purposes.

