"""
Quick script to check benchmark evaluation progress.
Run this in a separate terminal to monitor progress.
"""
import os
import json
from datetime import datetime
from pathlib import Path

def check_progress():
    results_dir = Path("benchmark_evaluator/results")
    
    if not results_dir.exists():
        print("Results directory not found!")
        return
    
    print("="*80)
    print("BENCHMARK EVALUATION PROGRESS")
    print("="*80)
    print(f"Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    benchmarks = ['mmlu', 'arc_challenge', 'gpqa_diamond', 'bbh', 'math', 'gsm8k']
    systems = ['bMAS', 'orig_bMAS', 'static_mas', 'cot']
    
    for benchmark in benchmarks:
        print(f"\n{benchmark.upper()}:")
        print("-" * 40)
        
        benchmark_complete = True
        for system in systems:
            result_file = results_dir / f"{benchmark}_{system}_results.json"
            
            if result_file.exists():
                try:
                    with open(result_file, 'r', encoding='utf-8') as f:
                        results = json.load(f)
                    
                    count = len(results)
                    last_update = datetime.fromtimestamp(result_file.stat().st_mtime)
                    
                    # Count correct answers
                    correct = sum(1 for r in results if r.get('correct', False))
                    accuracy = (correct / count * 100) if count > 0 else 0
                    
                    print(f"  {system:<15} {count:>3} problems | "
                          f"Accuracy: {accuracy:>5.1f}% | "
                          f"Last update: {last_update.strftime('%H:%M:%S')}")
                except Exception as e:
                    print(f"  {system:<15} Error reading file: {e}")
            else:
                print(f"  {system:<15} Not started")
                benchmark_complete = False
        
        if benchmark_complete:
            print(f"  [COMPLETE] {benchmark}")
    
    print("\n" + "="*80)
    print("Note: Run this script periodically to check progress.")
    print("="*80)

if __name__ == "__main__":
    check_progress()

