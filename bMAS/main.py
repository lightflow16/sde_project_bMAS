"""
Main entry point for the LbMAS system.
"""
import argparse
import sys
import os

# Add current directory and root to path for imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.dirname(_current_dir)
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

from experiment_runner.run_experiment import run_single_experiment, run_batch_experiments
from experiment_runner.data_loader import load_dataset, create_sample_dataset
import config


def main():
    parser = argparse.ArgumentParser(description="LbMAS: Blackboard-based LLM Multi-Agent System")
    parser.add_argument("--mode", choices=["single", "batch", "sample"], default="single",
                       help="Execution mode: single problem, batch from dataset, or create sample dataset")
    parser.add_argument("--problem", type=str, help="Problem/question to solve (for single mode)")
    parser.add_argument("--dataset", type=str, help="Path to dataset JSON file (for batch mode)")
    parser.add_argument("--max-rounds", type=int, default=config.MAX_ROUNDS,
                       help=f"Maximum number of rounds (default: {config.MAX_ROUNDS})")
    parser.add_argument("--output-dir", type=str, default=config.RESULTS_DIR,
                       help=f"Output directory for results (default: {config.RESULTS_DIR})")
    
    args = parser.parse_args()
    
    if args.mode == "sample":
        print("Creating sample dataset...")
        create_sample_dataset()
        print("Sample dataset created at bMAS/datasets/sample.json")
        return
    
    if args.mode == "single":
        if not args.problem:
            print("Error: --problem is required for single mode")
            parser.print_help()
            sys.exit(1)
        
        print(f"Running single experiment on problem: {args.problem}")
        result = run_single_experiment(args.problem, max_rounds=args.max_rounds)
        
        print("\n" + "="*60)
        print("Experiment Result")
        print("="*60)
        print(f"Final Answer: {result.get('final_answer', 'N/A')}")
        print(f"Solution Ready: {result.get('is_solution_ready', False)}")
        print(f"Total Tokens: {result.get('total_tokens', 0)}")
        print(f"Rounds Executed: {len(result.get('rounds', []))}")
        print("="*60)
    
    elif args.mode == "batch":
        if not args.dataset:
            print("Error: --dataset is required for batch mode")
            parser.print_help()
            sys.exit(1)
        
        print(f"Loading dataset from {args.dataset}...")
        tasks = load_dataset(args.dataset)
        print(f"Loaded {len(tasks)} tasks")
        
        print(f"Running batch experiments (max {args.max_rounds} rounds per task)...")
        results = run_batch_experiments(tasks, max_rounds=args.max_rounds, output_dir=args.output_dir)
        
        print(f"\nResults saved to {args.output_dir}/")


if __name__ == "__main__":
    main()

