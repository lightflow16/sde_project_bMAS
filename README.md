# LbMAS: Blackboard-based LLM Multi-Agent System

A research implementation of a blackboard-based LLM multi-agent system (LbMAS) based on the paper "Exploring Advanced LLM Multi-Agent Systems Based on Blackboard Architecture."

This repository contains the main LbMAS implementation along with comparison frameworks (Static MAS, Chain-of-Thought) for experimental evaluation.

## Citation

If you use this implementation in your research, please cite the original paper:

```bibtex
@article{han2025exploring,
  title={Exploring Advanced LLM Multi-Agent Systems Based on Blackboard Architecture},
  author={Han, Bochen and Zhang, Songmao},
  journal={arXiv preprint arXiv:2507.01701},
  year={2025},
  url={https://arxiv.org/abs/2507.01701}
}
```

**Paper:** [Exploring Advanced LLM Multi-Agent Systems Based on Blackboard Architecture](https://arxiv.org/abs/2507.01701)

**Authors:** Bochen Han, Songmao Zhang

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Features

- **Blackboard Architecture**: Shared memory system with public and private spaces for agent collaboration
- **Dynamic Agent Generation**: Expert agents generated based on problem domain
- **Predefined Agents**: Planner, Decider, Critic, Cleaner, ConflictResolver
- **Control Unit**: LLM-based intelligent agent scheduling
- **Multi-Round Execution**: Iterative problem-solving with configurable rounds
- **Token Tracking**: Monitor LLM API usage and costs
- **Experiment Runner**: Batch processing with evaluation and metrics
- **Comparison Frameworks**: Includes Static MAS and Chain-of-Thought implementations for comparison

## Prerequisites

- **Python 3.8+** (Python 3.9+ recommended)
- **Ollama** (recommended for local models) OR API keys for remote models
- **Git** (for cloning the repository)

### Installing Ollama (Recommended)

**Windows:**
1. Download from [https://ollama.ai/download](https://ollama.ai/download)
2. Run the installer
3. Open PowerShell/Command Prompt and run: `ollama serve`

**Linux/Mac:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
```

**Pull required models:**
```bash
ollama pull llama3.1:8b
ollama pull gemma3:4b
# Add other models as needed (see Configuration section)
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd bMAS
   ```

2. **Create a virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r bMAS/requirements.txt
   ```

4. **Verify installation:**
   ```bash
   python bMAS/test_ollama.py
   ```

## Configuration

### Option 1: Using Ollama (Recommended - Local Models)

Ollama is enabled by default. Make sure Ollama is running:
```bash
ollama serve
```

The system will automatically use your local Ollama models. No additional configuration needed!

### Option 2: Using API Models (Remote)

If you prefer to use remote API models, create a `.env` file in the project root:

```env
USE_OLLAMA=false
OPENAI_API_KEY=your_openai_key_here
HUGGINGFACE_API_KEY=your_huggingface_key_here
```

### Model Configuration

Edit `config.py` to customize models:

- **Ollama Models** (default): `gpt-oss:20b`, `gemma3:4b`, `cogito:14b`, `llama3.1:8b`
- **API Models** (fallback): `meta-llama/Llama-3.1-70B-Instruct`, `Qwen/Qwen2.5-72B-Instruct`

You can also adjust:
- `TEMPERATURE`: Default 0.7
- `MAX_ROUNDS`: Default 4 rounds per experiment
- Output directories

## Quick Start

### Test with a Simple Problem

```bash
python bMAS/main.py --mode single --problem "What is 2 + 2? Explain your reasoning."
```

### Run Example Script

```bash
python bMAS/example.py
```

### Create a Sample Dataset

```bash
python bMAS/main.py --mode sample
```

This creates a sample dataset at `bMAS/datasets/sample.json`.

## Usage

### Single Problem Mode

Run a single experiment on a problem:

```bash
python bMAS/main.py --mode single --problem "Your problem here" --max-rounds 4
```

**Example:**
```bash
python bMAS/main.py --mode single --problem "In the land of Ink, the money system is unique. One Trinket is equal to 4 Blinkets, and 3 Blinkets are equal to 7 Drinkets. In Trinkets, what is the value of 56 Drinkets?"
```

### Batch Mode

Run experiments on a dataset:

```bash
python bMAS/main.py --mode batch --dataset bMAS/datasets/sample.json --max-rounds 4
```

**Dataset Format:**
```json
[
  {
    "id": "task_1",
    "problem": "Your problem statement here",
    "ground_truth": "Expected answer (optional)"
  },
  {
    "id": "task_2",
    "problem": "Another problem",
    "ground_truth": "Another answer"
  }
]
```

### Comparison Experiments

Run comparison experiments across different MAS frameworks:

```bash
# Run all test cases comparison
python run_all_cases_comparison.py

# Run hard cases only
python run_hard_cases_comparison.py

# Run all MAS comparison
python run_all_mas_comparison.py
```

## Project Structure

```
bMAS/
├── bMAS/                      # Main LbMAS implementation
│   ├── agents/                # Agent implementations
│   │   ├── base_agent.py      # Base agent class
│   │   ├── predefined.py      # Planner, Decider, Critic, etc.
│   │   └── generated_expert.py # Dynamically generated experts
│   ├── blackboard/            # Blackboard shared memory
│   │   └── blackboard.py
│   ├── control_unit/          # Control unit for scheduling
│   │   └── scheduler.py
│   ├── experiment_runner/     # Experiment execution
│   │   ├── run_experiment.py
│   │   └── data_loader.py
│   ├── llm_integration/       # LLM API integration
│   │   └── api.py
│   ├── prompts/               # Prompt templates
│   ├── datasets/              # Dataset storage
│   ├── outputs/               # Experiment outputs
│   ├── results/               # Results and metrics
│   ├── main.py                # Main entry point
│   ├── example.py             # Example usage script
│   ├── test_ollama.py         # Ollama connection test
│   └── requirements.txt       # Python dependencies
│
├── static_mas/                # Static MAS comparison framework
├── cot/                       # Chain-of-Thought comparison framework
├── orig_impl_bMAS/            # Original bMAS implementation (for comparison)
├── config.py                  # Global configuration
├── run_all_cases_comparison.py # Comparison experiment runner
└── README.md                  # This file
```

## Testing

### Test Ollama Connection

Verify that Ollama is set up correctly:

```bash
python bMAS/test_ollama.py
```

This will:
- Check if Ollama is running
- List available models
- Test a simple model call

### Run Easy Test Cases

```bash
python bMAS/test_easy_cases.py
```

### Verify Results

```bash
python bMAS/verify_results.py
```

## Troubleshooting

### Ollama Connection Issues

**Problem:** `Cannot connect to Ollama`

**Solution:**
1. Make sure Ollama is running: `ollama serve`
2. Check if Ollama is accessible: `curl http://localhost:11434/api/tags`
3. Verify the base URL in `config.py` matches your Ollama setup

### Missing Models

**Problem:** `Model not found`

**Solution:**
1. Pull the required model: `ollama pull llama3.1:8b`
2. Check available models: `ollama list`
3. Update `config.py` with models you have available

### Import Errors

**Problem:** `ModuleNotFoundError`

**Solution:**
1. Make sure you're in the project root directory
2. Activate your virtual environment
3. Reinstall dependencies: `pip install -r bMAS/requirements.txt`

### API Key Issues

**Problem:** API calls failing when using remote models

**Solution:**
1. Create a `.env` file in the project root
2. Add your API keys:
   ```env
   OPENAI_API_KEY=your_key
   HUGGINGFACE_API_KEY=your_key
   ```
3. Make sure `USE_OLLAMA=false` in `.env` if using APIs

### Performance Issues

**Problem:** Slow execution or timeouts

**Solution:**
1. Reduce `MAX_ROUNDS` in `config.py` (default: 4)
2. Use smaller/faster models
3. Check your network connection if using API models
4. Ensure sufficient system resources for local models

## Output Files

Results are saved in:
- **Traces**: `bMAS/outputs/trace_*.json` - Detailed execution traces
- **Reports**: `bMAS/outputs/report_*.txt` - Human-readable reports
- **Metrics**: `metrics_outputs/*.json` - Performance metrics

## Contributing

This is a research project. For questions or issues:
1. Check existing documentation in the `bMAS/` directory
2. Review comparison and improvement documents
3. Test with `test_ollama.py` first

## License

This implementation is based on research and is for educational/research purposes.

## Additional Resources

- See `bMAS/README.md` for detailed LbMAS documentation
- Check `bMAS/LOGGING_GUIDE.md` for logging configuration
- Review `METRICS_TRACKING_GUIDE.md` for metrics tracking
- See comparison documents for framework analysis

---

**Note:** Make sure Ollama is running (`ollama serve`) before executing experiments, or configure API keys if using remote models.

