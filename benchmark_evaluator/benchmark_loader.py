"""
Benchmark dataset loader for standard LLM evaluation benchmarks.

Supports loading datasets from Hugging Face:
- MMLU (Massive Multitask Language Understanding)
- ARC-Challenge
- GPQA-Diamond
- BBH (BIG-Bench Hard)
- MATH
- GSM8K
"""
import os
import json
from typing import Dict, Any, List, Optional
from datasets import load_dataset
import re


class BenchmarkLoader:
    """Loader for benchmark datasets."""
    
    # Benchmark configurations
    BENCHMARKS = {
        "mmlu": {
            "hf_name": "cais/mmlu",
            "subset": "all",
            "split": "test",
            "question_field": "question",
            "answer_field": "answer",
            "choices_field": "choices",
            "type": "multiple_choice",
            "num_problems": 1140
        },
        "arc_challenge": {
            "hf_name": "allenai/ai2_arc",
            "subset": "ARC-Challenge",
            "split": "test",
            "question_field": "question",
            "answer_field": "answerKey",
            "choices_field": "choices",
            "type": "multiple_choice",
            "num_problems": 1172
        },
        "gpqa_diamond": {
            "hf_name": "google-research-datasets/gpqa",
            "subset": "diamond",
            "split": "test",
            "question_field": "question",
            "answer_field": "correct_answer",
            "choices_field": "choices",
            "type": "multiple_choice",
            "num_problems": 198
        },
        "bbh": {
            "hf_name": "allenai/bbh",
            "subset": None,
            "split": "test",
            "question_field": "input",
            "answer_field": "target",
            "choices_field": None,
            "type": "free_form",
            "num_problems": 250  # Approximate, varies by task
        },
        "math": {
            "hf_name": "lighteval/MATH",
            "subset": None,
            "split": "test",
            "question_field": "problem",
            "answer_field": "solution",
            "choices_field": None,
            "type": "free_form",
            "num_problems": 500
        },
        "gsm8k": {
            "hf_name": "gsm8k",
            "subset": "main",
            "split": "test",
            "question_field": "question",
            "answer_field": "answer",
            "choices_field": None,
            "type": "free_form",
            "num_problems": 1319
        }
    }
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize benchmark loader."""
        self.cache_dir = cache_dir or os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "datasets")
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def load_benchmark(self, benchmark_name: str, max_samples: Optional[int] = None,
                      random_sample: bool = True) -> List[Dict[str, Any]]:
        """
        Load a benchmark dataset.
        
        Args:
            benchmark_name: Name of benchmark (mmlu, arc_challenge, gpqa_diamond, bbh, math, gsm8k)
            max_samples: Maximum number of samples to load (None for all)
            random_sample: If True and max_samples is set, randomly sample problems instead of taking first N
            
        Returns:
            List of problem dictionaries with standardized format
        """
        if benchmark_name not in self.BENCHMARKS:
            raise ValueError(f"Unknown benchmark: {benchmark_name}. Available: {list(self.BENCHMARKS.keys())}")
        
        config = self.BENCHMARKS[benchmark_name]
        
        try:
            # Load dataset from Hugging Face
            if config["subset"]:
                dataset = load_dataset(
                    config["hf_name"],
                    config["subset"],
                    split=config["split"],
                    cache_dir=self.cache_dir
                )
            else:
                dataset = load_dataset(
                    config["hf_name"],
                    split=config["split"],
                    cache_dir=self.cache_dir
                )
            
            # Convert to standardized format
            problems = []
            dataset_size = len(dataset)
            
            # Determine indices to use
            if max_samples and max_samples < dataset_size:
                if random_sample:
                    # Randomly sample indices
                    import random
                    indices = random.sample(range(dataset_size), max_samples)
                    indices.sort()  # Keep sorted for reproducibility
                else:
                    # Take first N
                    indices = list(range(max_samples))
            else:
                # Use all
                indices = list(range(dataset_size))
            
            # Convert to standardized format
            for idx in indices:
                item = dataset[idx]
                problem = self._standardize_problem(item, config, benchmark_name, idx)
                if problem:
                    problems.append(problem)
            
            if max_samples and random_sample:
                print(f"Randomly sampled {len(problems)} problems from {dataset_size} total")
            
            return problems
            
        except Exception as e:
            print(f"Error loading benchmark {benchmark_name}: {e}")
            print(f"Attempting to load from local cache or fallback...")
            # Try to load from local file if available
            local_path = f"benchmark_evaluator/datasets/{benchmark_name}.json"
            if os.path.exists(local_path):
                with open(local_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            raise
    
    def _standardize_problem(self, item: Dict[str, Any], config: Dict[str, Any], 
                           benchmark_name: str, idx: int) -> Optional[Dict[str, Any]]:
        """Convert dataset item to standardized problem format."""
        try:
            problem_text = item.get(config["question_field"], "")
            answer = item.get(config["answer_field"], "")
            
            if not problem_text:
                return None
            
            # Format problem text
            formatted_problem = problem_text
            
            # Add choices for multiple-choice questions
            if config["type"] == "multiple_choice" and config["choices_field"]:
                choices = item.get(config["choices_field"], [])
                if isinstance(choices, list) and len(choices) > 0:
                    # Handle different choice formats
                    if isinstance(choices[0], dict):
                        # Format: [{"text": "...", "label": "A"}, ...]
                        choice_texts = []
                        for i, choice in enumerate(choices):
                            label = choice.get("label", chr(65 + i))  # A, B, C, D
                            text = choice.get("text", str(choice))
                            choice_texts.append(f"{label}) {text}")
                    else:
                        # Format: ["choice1", "choice2", ...]
                        choice_texts = [f"{chr(65 + i)}) {choice}" for i, choice in enumerate(choices)]
                    
                    formatted_problem += "\n\n" + "\n".join(choice_texts)
            
            # Extract answer for multiple choice
            if config["type"] == "multiple_choice":
                # Normalize answer to single letter (A, B, C, D)
                answer = str(answer).strip().upper()
                
                # Handle numeric indices (0, 1, 2, 3) -> (A, B, C, D)
                if answer.isdigit():
                    idx = int(answer)
                    if 0 <= idx <= 3:
                        answer = chr(65 + idx)  # 0->A, 1->B, 2->C, 3->D
                
                # If still not a single letter, try to extract
                if len(answer) > 1:
                    # Try to extract first letter
                    match = re.search(r'([A-D])', answer)
                    if match:
                        answer = match.group(1)
                    # If no letter found but it's a number, convert it
                    elif answer.isdigit():
                        idx = int(answer)
                        if 0 <= idx <= 3:
                            answer = chr(65 + idx)
            
            # Extract answer for free-form (MATH, GSM8K)
            if config["type"] == "free_form":
                if benchmark_name == "gsm8k":
                    # GSM8K format: "answer: 42" or just "42"
                    answer_match = re.search(r'(\d+(?:\.\d+)?)', str(answer))
                    if answer_match:
                        answer = answer_match.group(1)
                elif benchmark_name == "math":
                    # MATH format: extract from solution or use boxed format
                    # Look for \boxed{...} or final number
                    boxed_match = re.search(r'\\boxed\{([^}]+)\}', str(answer))
                    if boxed_match:
                        answer = boxed_match.group(1).strip()
                    else:
                        # Extract last number
                        numbers = re.findall(r'\d+(?:\.\d+)?', str(answer))
                        if numbers:
                            answer = numbers[-1]
            
            return {
                "id": f"{benchmark_name}_{idx}",
                "benchmark": benchmark_name,
                "problem": formatted_problem,
                "ground_truth": answer,
                "type": config["type"],
                "original_data": item  # Keep original for reference
            }
            
        except Exception as e:
            print(f"Error standardizing problem {idx}: {e}")
            return None
    
    def save_benchmark_locally(self, benchmark_name: str, problems: List[Dict[str, Any]]):
        """Save benchmark to local JSON file for offline use."""
        os.makedirs("benchmark_evaluator/datasets", exist_ok=True)
        filepath = f"benchmark_evaluator/datasets/{benchmark_name}.json"
        with open(filepath, 'w', encoding='utf-8', errors='replace') as f:
            json.dump(problems, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(problems)} problems to {filepath}")
    
    @staticmethod
    def list_benchmarks() -> List[str]:
        """List available benchmarks."""
        return list(BenchmarkLoader.BENCHMARKS.keys())

