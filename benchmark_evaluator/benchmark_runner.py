"""
Benchmark runner that executes all 4 MAS systems on benchmark datasets.
"""
import os
import sys
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict

# Add parent directory to path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.dirname(_current_dir)
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

# Import MAS systems
from bMAS.experiment_runner.run_experiment import run_single_experiment as run_bmas
from orig_impl_bMAS.experiment_runner.run_experiment import run_single_experiment as run_orig_bmas
from static_mas.run_experiment import run_static_experiment
from cot.run_experiment import run_cot_experiment

# Import benchmark utilities
from benchmark_evaluator.answer_evaluator import AnswerEvaluator
from benchmark_evaluator.benchmark_loader import BenchmarkLoader

# Import metrics tracker
try:
    from metrics_tracker import MetricsTracker
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    MetricsTracker = None


class BenchmarkRunner:
    """Runner for executing benchmarks across all MAS systems."""
    
    def __init__(self, output_dir: str = "benchmark_evaluator/results"):
        """Initialize benchmark runner."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.loader = BenchmarkLoader()
        self.evaluator = AnswerEvaluator()
        
        # System configurations
        self.systems = {
            "bMAS": {
                "runner": self._run_bmas,
                "display_name": "bMAS (LbMAS)"
            },
            "orig_bMAS": {
                "runner": self._run_orig_bmas,
                "display_name": "orig_impl_bMAS"
            },
            "static_mas": {
                "runner": self._run_static_mas,
                "display_name": "Static MAS"
            },
            "cot": {
                "runner": self._run_cot,
                "display_name": "Chain-of-Thought (CoT)"
            }
        }
    
    def _run_bmas(self, problem: str, ground_truth: str, problem_type: str, 
                  problem_id: str, max_rounds: int = 4) -> Dict[str, Any]:
        """Run bMAS system."""
        # Don't create logger for benchmark runs to avoid file I/O overhead
        # Results are aggregated in benchmark_evaluator/results/
        start_time = time.time()
        result = run_bmas(
            problem=problem,
            max_rounds=max_rounds,
            ground_truth=ground_truth,
            enable_logging=False,  # Disable logging to avoid per-problem file I/O
            logger=None
        )
        execution_time = time.time() - start_time
        
        final_answer = result.get('final_answer', '')
        is_correct, reason = self.evaluator.evaluate_answer(
            final_answer, ground_truth, problem_type
        )
        
        return {
            'system': 'bMAS',
            'problem_id': problem_id,
            'final_answer': final_answer,
            'ground_truth': ground_truth,
            'correct': is_correct,
            'evaluation_reason': reason,
            'total_tokens': result.get('total_tokens', 0),
            'prompt_tokens': result.get('prompt_tokens', 0),
            'completion_tokens': result.get('completion_tokens', 0),
            'execution_time': execution_time,
            'rounds': len(result.get('rounds', [])),
            'solution_ready': result.get('is_solution_ready', False),
            'consensus_reached': result.get('is_solution_ready', False)
        }
    
    def _run_orig_bmas(self, problem: str, ground_truth: str, problem_type: str,
                      problem_id: str, max_rounds: int = 4) -> Dict[str, Any]:
        """Run orig_impl_bMAS system."""
        # Don't create logger for benchmark runs to avoid file I/O overhead
        # Results are aggregated in benchmark_evaluator/results/
        start_time = time.time()
        result = run_orig_bmas(
            problem=problem,
            max_rounds=max_rounds,
            ground_truth=ground_truth,
            enable_logging=False,  # Disable logging to avoid per-problem file I/O
            logger=None
        )
        execution_time = time.time() - start_time
        
        final_answer = result.get('final_answer', '')
        is_correct, reason = self.evaluator.evaluate_answer(
            final_answer, ground_truth, problem_type
        )
        
        return {
            'system': 'orig_bMAS',
            'problem_id': problem_id,
            'final_answer': final_answer,
            'ground_truth': ground_truth,
            'correct': is_correct,
            'evaluation_reason': reason,
            'total_tokens': result.get('total_tokens', 0),
            'prompt_tokens': result.get('prompt_tokens', 0),
            'completion_tokens': result.get('completion_tokens', 0),
            'execution_time': execution_time,
            'rounds': len(result.get('rounds', [])),
            'solution_ready': result.get('is_solution_ready', False),
            'consensus_reached': result.get('is_solution_ready', False)
        }
    
    def _run_static_mas(self, problem: str, ground_truth: str, problem_type: str,
                       problem_id: str, max_rounds: int = 4) -> Dict[str, Any]:
        """Run Static MAS system."""
        # Disable logging for benchmark runs to avoid per-problem file I/O
        start_time = time.time()
        result = run_static_experiment(
            problem=problem,
            ground_truth=ground_truth,
            aggregation_method="majority_vote",
            enable_logging=False  # Disable logging to avoid per-problem file I/O
        )
        execution_time = time.time() - start_time
        
        final_answer = result.get('final_answer', '')
        is_correct, reason = self.evaluator.evaluate_answer(
            final_answer, ground_truth, problem_type
        )
        
        return {
            'system': 'static_mas',
            'problem_id': problem_id,
            'final_answer': final_answer,
            'ground_truth': ground_truth,
            'correct': is_correct,
            'evaluation_reason': reason,
            'total_tokens': result.get('total_tokens', 0),
            'prompt_tokens': result.get('prompt_tokens', 0),
            'completion_tokens': result.get('completion_tokens', 0),
            'execution_time': execution_time,
            'rounds': 1,  # Static MAS is single-pass
            'solution_ready': True,
            'consensus_reached': True,
            'num_agents': len(result.get('agents', []))
        }
    
    def _run_cot(self, problem: str, ground_truth: str, problem_type: str,
                problem_id: str, max_rounds: int = 4) -> Dict[str, Any]:
        """Run Chain-of-Thought baseline."""
        # Disable logging for benchmark runs to avoid per-problem file I/O
        start_time = time.time()
        result = run_cot_experiment(
            problem=problem,
            ground_truth=ground_truth,
            enable_logging=False  # Disable logging to avoid per-problem file I/O
        )
        execution_time = time.time() - start_time
        
        final_answer = result.get('final_answer', '')
        is_correct, reason = self.evaluator.evaluate_answer(
            final_answer, ground_truth, problem_type
        )
        
        return {
            'system': 'cot',
            'problem_id': problem_id,
            'final_answer': final_answer,
            'ground_truth': ground_truth,
            'correct': is_correct,
            'evaluation_reason': reason,
            'total_tokens': result.get('tokens_used', 0),
            'prompt_tokens': result.get('prompt_tokens', 0),
            'completion_tokens': result.get('completion_tokens', 0),
            'execution_time': execution_time,
            'rounds': 1,  # CoT is single-pass
            'solution_ready': True,
            'consensus_reached': True
        }
    
    def run_benchmark(self, benchmark_name: str, systems: Optional[List[str]] = None,
                     max_problems: Optional[int] = None, max_rounds: int = 4,
                     save_intermediate: bool = True, random_sample: bool = True) -> Dict[str, Any]:
        """
        Run a benchmark across all systems.
        
        Args:
            benchmark_name: Name of benchmark to run
            systems: List of system names to run (None for all)
            max_problems: Maximum number of problems to evaluate
            max_rounds: Maximum rounds for iterative systems
            save_intermediate: Whether to save intermediate results
            
        Returns:
            Dictionary with results for all systems
        """
        print(f"\n{'='*80}")
        print(f"Loading benchmark: {benchmark_name}")
        print(f"{'='*80}")
        
        # Load benchmark
        problems = self.loader.load_benchmark(
            benchmark_name, 
            max_samples=max_problems,
            random_sample=random_sample
        )
        print(f"Loaded {len(problems)} problems")
        
        if max_problems and len(problems) < max_problems:
            print(f"Note: Only {len(problems)} problems available (requested {max_problems})")
        
        # Select systems to run
        systems_to_run = systems if systems else list(self.systems.keys())
        
        # Run each system
        all_results = {}
        
        for system_name in systems_to_run:
            if system_name not in self.systems:
                print(f"Warning: Unknown system {system_name}, skipping")
                continue
            
            print(f"\n{'='*80}", flush=True)
            print(f"Running {self.systems[system_name]['display_name']} on {benchmark_name}", flush=True)
            print(f"{'='*80}", flush=True)
            
            system_results = []
            runner = self.systems[system_name]['runner']
            
            for idx, problem_data in enumerate(problems):
                print(f"\n[{idx+1}/{len(problems)}] Problem {problem_data['id']}", flush=True)
                
                try:
                    result = runner(
                        problem=problem_data['problem'],
                        ground_truth=problem_data['ground_truth'],
                        problem_type=problem_data['type'],
                        problem_id=problem_data['id'],
                        max_rounds=max_rounds
                    )
                    
                    result['benchmark'] = benchmark_name
                    result['problem_index'] = idx
                    system_results.append(result)
                    
                    # Use ASCII-safe status symbols to avoid encoding issues
                    status = "[OK]" if result['correct'] else "[X]"
                    try:
                        print(f"  {status} Answer: {result['final_answer'][:50]}... "
                              f"({result['total_tokens']} tokens, {result['execution_time']:.2f}s)", flush=True)
                    except UnicodeEncodeError:
                        # Fallback for systems with encoding issues
                        answer_preview = str(result['final_answer'][:50]).encode('ascii', errors='replace').decode('ascii')
                        print(f"  {status} Answer: {answer_preview}... "
                              f"({result['total_tokens']} tokens, {result['execution_time']:.2f}s)", flush=True)
                    
                    # Save intermediate results
                    if save_intermediate and (idx + 1) % 10 == 0:
                        self._save_intermediate_results(
                            benchmark_name, system_name, system_results
                        )
                
                except Exception as e:
                    print(f"  ERROR: {e}")
                    import traceback
                    traceback.print_exc()
                    # Add error result
                    system_results.append({
                        'system': system_name,
                        'problem_id': problem_data['id'],
                        'benchmark': benchmark_name,
                        'problem_index': idx,
                        'error': str(e),
                        'correct': False
                    })
            
            all_results[system_name] = system_results
            
            # Save final results for this system
            self._save_results(benchmark_name, system_name, system_results)
        
        # Aggregate results
        summary = self._aggregate_results(benchmark_name, all_results)
        
        # Save summary
        self._save_summary(benchmark_name, summary, all_results)
        
        return {
            'benchmark': benchmark_name,
            'summary': summary,
            'results': all_results
        }
    
    def _save_intermediate_results(self, benchmark_name: str, system_name: str,
                                   results: List[Dict[str, Any]]):
        """Save intermediate results."""
        filepath = os.path.join(
            self.output_dir,
            f"{benchmark_name}_{system_name}_intermediate_{len(results)}.json"
        )
        with open(filepath, 'w', encoding='utf-8', errors='replace') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    
    def _save_results(self, benchmark_name: str, system_name: str,
                     results: List[Dict[str, Any]]):
        """Save results for a system."""
        filepath = os.path.join(
            self.output_dir,
            f"{benchmark_name}_{system_name}_results.json"
        )
        with open(filepath, 'w', encoding='utf-8', errors='replace') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nSaved results to {filepath}")
    
    def _aggregate_results(self, benchmark_name: str,
                          all_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Aggregate results across all systems."""
        summary = {
            'benchmark': benchmark_name,
            'timestamp': datetime.now().isoformat(),
            'systems': {}
        }
        
        for system_name, results in all_results.items():
            if not results:
                continue
            
            # Filter out error results
            valid_results = [r for r in results if 'error' not in r]
            
            if not valid_results:
                continue
            
            # Calculate metrics
            total = len(valid_results)
            correct = sum(1 for r in valid_results if r.get('correct', False))
            accuracy = (correct / total * 100) if total > 0 else 0
            
            total_tokens = sum(r.get('total_tokens', 0) for r in valid_results)
            prompt_tokens = sum(r.get('prompt_tokens', 0) for r in valid_results)
            completion_tokens = sum(r.get('completion_tokens', 0) for r in valid_results)
            
            total_time = sum(r.get('execution_time', 0) for r in valid_results)
            avg_time = total_time / total if total > 0 else 0
            
            avg_rounds = sum(r.get('rounds', 1) for r in valid_results) / total if total > 0 else 1
            consensus_rate = sum(1 for r in valid_results if r.get('consensus_reached', False)) / total if total > 0 else 0
            
            summary['systems'][system_name] = {
                'display_name': self.systems[system_name]['display_name'],
                'total_problems': total,
                'correct': correct,
                'incorrect': total - correct,
                'accuracy': accuracy,
                'total_tokens': total_tokens,
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'avg_tokens_per_problem': total_tokens / total if total > 0 else 0,
                'total_time': total_time,
                'avg_time_per_problem': avg_time,
                'avg_rounds': avg_rounds,
                'consensus_rate': consensus_rate * 100
            }
        
        return summary
    
    def _save_summary(self, benchmark_name: str, summary: Dict[str, Any],
                     all_results: Dict[str, List[Dict[str, Any]]]):
        """Save summary report."""
        filepath = os.path.join(
            self.output_dir,
            f"{benchmark_name}_summary.json"
        )
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # Also save human-readable summary
        txt_filepath = os.path.join(
            self.output_dir,
            f"{benchmark_name}_summary.txt"
        )
        with open(txt_filepath, 'w', encoding='utf-8', errors='replace') as f:
            f.write("="*80 + "\n")
            f.write(f"BENCHMARK EVALUATION SUMMARY: {benchmark_name.upper()}\n")
            f.write("="*80 + "\n\n")
            f.write(f"Timestamp: {summary['timestamp']}\n\n")
            
            f.write("SYSTEM PERFORMANCE:\n")
            f.write("-"*80 + "\n")
            f.write(f"{'System':<25} {'Accuracy':<12} {'Avg Tokens':<15} {'Avg Time':<12} {'Avg Rounds':<12}\n")
            f.write("-"*80 + "\n")
            
            for system_name, metrics in summary['systems'].items():
                f.write(f"{metrics['display_name']:<25} "
                       f"{metrics['accuracy']:.2f}%{'':<6} "
                       f"{metrics['avg_tokens_per_problem']:.0f}{'':<9} "
                       f"{metrics['avg_time_per_problem']:.2f}s{'':<6} "
                       f"{metrics['avg_rounds']:.2f}{'':<8}\n")
            
            f.write("\n" + "="*80 + "\n")
        
        print(f"\nSaved summary to {filepath} and {txt_filepath}")

