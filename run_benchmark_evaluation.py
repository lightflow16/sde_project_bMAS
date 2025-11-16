"""
Main script for running benchmark evaluations across all 4 MAS systems.

Usage:
    python run_benchmark_evaluation.py --benchmark mmlu --max-problems 10
    python run_benchmark_evaluation.py --all --max-problems 50
    python run_benchmark_evaluation.py --generate-tables
"""
import argparse
import sys
import os
from typing import List, Optional

# Add current directory to path
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from benchmark_evaluator.benchmark_loader import BenchmarkLoader
from benchmark_evaluator.benchmark_runner import BenchmarkRunner
from benchmark_evaluator.results_aggregator import ResultsAggregator


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark evaluation for MAS systems",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run MMLU benchmark with 5 sample problems (recommended for testing)
  python run_benchmark_evaluation.py --benchmark mmlu --sample 5
  
  # Run MATH benchmark with 10 problems (default)
  python run_benchmark_evaluation.py --benchmark math
  
  # Run all benchmarks with 5 problems each (quick test)
  python run_benchmark_evaluation.py --all --sample 5
  
  # Run specific systems on MATH benchmark
  python run_benchmark_evaluation.py --benchmark math --systems bMAS static_mas --sample 10
  
  # Generate comparison tables from existing results
  python run_benchmark_evaluation.py --generate-tables
  
Available benchmarks:
  - mmlu (Massive Multitask Language Understanding)
  - arc_challenge (ARC-Challenge)
  - gpqa_diamond (GPQA-Diamond)
  - bbh (BIG-Bench Hard)
  - math (MATH dataset)
  - gsm8k (GSM8K dataset)
        """
    )
    
    parser.add_argument(
        '--benchmark',
        type=str,
        choices=['mmlu', 'arc_challenge', 'gpqa_diamond', 'bbh', 'math', 'gsm8k'],
        help='Benchmark to run'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all benchmarks'
    )
    
    parser.add_argument(
        '--systems',
        nargs='+',
        choices=['bMAS', 'orig_bMAS', 'static_mas', 'cot'],
        help='Systems to run (default: all)'
    )
    
    parser.add_argument(
        '--max-problems',
        type=int,
        default=10,
        help='Maximum number of problems to evaluate per benchmark (default: 10 for quick testing)'
    )
    
    parser.add_argument(
        '--sample',
        type=int,
        default=None,
        help='Alias for --max-problems (for convenience)'
    )
    
    parser.add_argument(
        '--max-rounds',
        type=int,
        default=4,
        help='Maximum rounds for iterative systems (default: 4)'
    )
    
    parser.add_argument(
        '--generate-tables',
        action='store_true',
        help='Generate comparison tables from existing results'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='benchmark_evaluator/results',
        help='Output directory for results (default: benchmark_evaluator/results)'
    )
    
    args = parser.parse_args()
    
    # Generate tables mode
    if args.generate_tables:
        print("Generating comparison tables from existing results...")
        aggregator = ResultsAggregator(results_dir=args.output_dir)
        
        benchmark_names = ['mmlu', 'arc_challenge', 'gpqa_diamond', 'bbh', 'math', 'gsm8k']
        benchmark_results = aggregator.aggregate_all_benchmarks(benchmark_names)
        
        if not benchmark_results:
            print("No benchmark results found. Please run evaluations first.")
            return
        
        # Generate performance table
        print("\nGenerating performance table...")
        perf_table = aggregator.generate_performance_table(
            benchmark_results,
            output_file=os.path.join(args.output_dir, 'table1_performance.txt')
        )
        print(perf_table)
        
        # Generate token cost table for MATH
        if 'math' in benchmark_results:
            print("\nGenerating token cost table for MATH...")
            token_table = aggregator.generate_token_cost_table(
                benchmark_results,
                'math',
                output_file=os.path.join(args.output_dir, 'table3_token_cost.txt')
            )
            print(token_table)
        
        # Generate markdown report
        print("\nGenerating markdown report...")
        report = aggregator.generate_markdown_report(
            benchmark_results,
            output_file=os.path.join(args.output_dir, 'benchmark_report.md')
        )
        
        print(f"\nTables generated in {args.output_dir}")
        return
    
    # Determine benchmarks to run
    if args.all:
        benchmarks_to_run = ['mmlu', 'arc_challenge', 'gpqa_diamond', 'bbh', 'math', 'gsm8k']
    elif args.benchmark:
        benchmarks_to_run = [args.benchmark]
    else:
        print("Error: Must specify --benchmark or --all")
        parser.print_help()
        sys.exit(1)
    
    # Use --sample if provided, otherwise use --max-problems
    max_problems = args.sample if args.sample is not None else args.max_problems
    
    # Warn if running without sample limit
    if max_problems is None or max_problems > 100:
        print("\n" + "!"*80)
        print("WARNING: Running with large number of problems or no limit!")
        print("This may take a very long time and consume many tokens.")
        print("Consider using --max-problems 10 or --sample 10 for testing.")
        print("!"*80 + "\n")
        response = input("Continue anyway? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Cancelled.")
            return
    
    # Initialize runner
    runner = BenchmarkRunner(output_dir=args.output_dir)
    
    # Run benchmarks
    all_results = {}
    
    for benchmark_name in benchmarks_to_run:
        print(f"\n{'='*80}")
        print(f"Starting evaluation: {benchmark_name}")
        print(f"{'='*80}")
        
        try:
            result = runner.run_benchmark(
                benchmark_name=benchmark_name,
                systems=args.systems,
                max_problems=max_problems,
                max_rounds=args.max_rounds,
                random_sample=True  # Randomly sample problems for better coverage
            )
            all_results[benchmark_name] = result['summary']
            
            print(f"\n{'='*80}")
            print(f"Completed: {benchmark_name}")
            print(f"{'='*80}")
            
            # Print summary
            if 'systems' in result['summary']:
                print("\nResults Summary:")
                print("-"*80)
                for system_name, metrics in result['summary']['systems'].items():
                    print(f"{metrics['display_name']:<25} "
                          f"Accuracy: {metrics['accuracy']:.2f}% | "
                          f"Avg Tokens: {metrics['avg_tokens_per_problem']:.0f} | "
                          f"Avg Time: {metrics['avg_time_per_problem']:.2f}s")
        
        except Exception as e:
            print(f"\nERROR running {benchmark_name}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Generate tables if we have results
    if all_results:
        print(f"\n{'='*80}")
        print("Generating comparison tables...")
        print(f"{'='*80}")
        
        aggregator = ResultsAggregator(results_dir=args.output_dir)
        
        # Generate performance table
        perf_table = aggregator.generate_performance_table(
            all_results,
            output_file=os.path.join(args.output_dir, 'table1_performance.txt')
        )
        print("\n" + perf_table)
        
        # Generate token cost table for MATH if available
        if 'math' in all_results:
            token_table = aggregator.generate_token_cost_table(
                all_results,
                'math',
                output_file=os.path.join(args.output_dir, 'table3_token_cost.txt')
            )
            print("\n" + token_table)
        
        # Generate markdown report
        aggregator.generate_markdown_report(
            all_results,
            output_file=os.path.join(args.output_dir, 'benchmark_report.md')
        )
        
        print(f"\nAll results saved to {args.output_dir}")
    
    print("\n" + "="*80)
    print("Benchmark evaluation complete!")
    print("="*80)


if __name__ == "__main__":
    main()

