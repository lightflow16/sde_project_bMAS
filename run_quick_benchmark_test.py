"""
Quick benchmark test script - runs a small sample from each benchmark.

This is a convenience script for quick testing with just a few problems.
"""
import sys
import os

# Add current directory to path
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from benchmark_evaluator.benchmark_runner import BenchmarkRunner
from benchmark_evaluator.results_aggregator import ResultsAggregator


def main():
    print("="*80)
    print("Quick Benchmark Test - Small Sample Evaluation")
    print("="*80)
    print("\nThis will run a small sample (5 problems) from each benchmark")
    print("to quickly validate all systems are working correctly.\n")
    
    # Skip confirmation in non-interactive mode
    try:
        response = input("Continue? (yes/no, default: yes): ")
        if response.lower() not in ['yes', 'y', '']:
            print("Cancelled.")
            return
    except EOFError:
        # Non-interactive mode, auto-confirm
        print("Non-interactive mode detected. Proceeding automatically...")
    
    # Run with small samples
    benchmarks = ['mmlu', 'arc_challenge', 'gpqa_diamond', 'bbh', 'math', 'gsm8k']
    sample_size = 5
    
    runner = BenchmarkRunner(output_dir="benchmark_evaluator/results")
    all_results = {}
    
    for benchmark_name in benchmarks:
        print(f"\n{'='*80}")
        print(f"Testing: {benchmark_name} ({sample_size} problems)")
        print(f"{'='*80}")
        
        try:
            result = runner.run_benchmark(
                benchmark_name=benchmark_name,
                systems=None,  # All systems
                max_problems=sample_size,
                max_rounds=4,
                random_sample=True
            )
            all_results[benchmark_name] = result['summary']
            
            # Print quick summary
            if 'systems' in result['summary']:
                print(f"\n{benchmark_name.upper()} Results:")
                for system_name, metrics in result['summary']['systems'].items():
                    print(f"  {metrics['display_name']:<25} Accuracy: {metrics['accuracy']:.1f}%")
        
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Generate summary
    if all_results:
        print(f"\n{'='*80}")
        print("Quick Test Summary")
        print(f"{'='*80}\n")
        
        aggregator = ResultsAggregator(results_dir="benchmark_evaluator/results")
        
        # Generate performance table
        perf_table = aggregator.generate_performance_table(all_results)
        print(perf_table)
        
        print(f"\n{'='*80}")
        print("Quick test complete!")
        print(f"Results saved to benchmark_evaluator/results/")
        print(f"{'='*80}")


if __name__ == "__main__":
    main()

