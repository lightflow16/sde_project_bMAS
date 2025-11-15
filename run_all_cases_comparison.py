"""
Run all test cases (Easy Cases A & B, Hard Cases C & D) across all 4 MAS setups and compare results.
"""
import sys
import os
import time

# Add paths for imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

# Import test functions from each MAS setup
from bMAS.experiment_runner.run_experiment import run_single_experiment as run_bmas
from bMAS.utils.logger import ExperimentLogger
from orig_impl_bMAS.experiment_runner.run_experiment import run_single_experiment as run_orig_bmas
from orig_impl_bMAS.utils.logger import ExperimentLogger as OrigExperimentLogger
from static_mas.run_experiment import run_static_experiment
from cot.run_experiment import run_cot_experiment

# Test case definitions
EASY_CASE_A = {
    "name": "Case A: Mathematical Problem",
    "problem": "In the land of Ink, the money system is unique. One Trinket is equal to 4 Blinkets, and 3 Blinkets are equal to 7 Drinkets. In Trinkets, what is the value of 56 Drinkets?",
    "ground_truth": "6 Trinkets"
}

EASY_CASE_B = {
    "name": "Case B: Common Knowledge Question",
    "problem": "Why is the sky blue? A) Because the molecules that compose the Earth's atmosphere have a blue-ish color. B) Because the sky reflects the color of the Earth's oceans. C) Because the atmosphere preferentially scatters short wavelengths. D) Because the Earth's atmosphere preferentially absorbs all other colors.",
    "ground_truth": "C"
}

HARD_CASE_C = {
    "name": "Case C: Theoretical Physics (Maxwell's Equations)",
    "problem": "In a parallel universe where a magnet can have an isolated North or South pole, Maxwell's equations look different. But, specifically, which of those equations are different?: A) The ones related to the circulation of the electric field and the divergence of the magnetic field. B) The ones related to the divergence and the curl of the magnetic field. C) The one related to the divergence of the magnetic field. D) The one related to the circulation of the magnetic field and the flux of the electric field.",
    "ground_truth": "A"
}

HARD_CASE_D = {
    "name": "Case D: Astrophysics (Supermassive Black Hole Location)",
    "problem": "A group of astronomers is using multiwavelength and spatially resolved data to determine the position of the Supermassive Black Hole (SMBH) in the circumnuclear region of a nearby Galaxy, they obtained the following results: The galactic optical surface-brightness profile is well fitted by a Sérsic component with Sérsic index (n) equal to 4. They find strongly emitting ionized and molecular Hydrogen in the spectra of the whole circumnuclear region and in particular they find a region toward the Northeast where the Ionized Hydrogen line profiles present a broad component (1000 km/s) that is blue-shifted with respect to the narrow component of the same line. Additionally, through the Southeast direction, they found a region with unresolved emission of the prohibited coronal line [NeV]. Which of the regions is the most probable to host the Supermassive Black Hole?: A) The region toward the Southeast, where the coronal line [NeV] emission is detected. B) The region toward the Northeast, where the broad component of the Ionized Hydrogen line is detected. C) The region toward the center, which corresponds to the peak of emission of the Sérsic Component. D) The region toward the Northwest, where the narrow component of the Ionized Hydrogen line is detected.",
    "ground_truth": "A"
}


def run_orig_bmas_test(problem, ground_truth, case_name, max_rounds=4):
    """Run case with orig_impl_bMAS (Original Implementation Prompts)."""
    print("\n" + "="*80)
    print(f"RUNNING orig_impl_bMAS (Original Prompts) - {case_name}")
    print("="*80)
    
    logger = OrigExperimentLogger(experiment_id=f"{case_name.lower().replace(' ', '_')}_orig_bmas")
    
    start_time = time.time()
    result = run_orig_bmas(
        problem=problem,
        max_rounds=max_rounds,
        ground_truth=ground_truth,
        enable_logging=True,
        logger=logger
    )
    execution_time = time.time() - start_time
    
    metrics = {
        'system': 'orig_impl_bMAS (Original Prompts)',
        'case': case_name,
        'final_answer': result.get('final_answer', 'N/A'),
        'correct': result.get('correct', False),
        'total_tokens': result.get('total_tokens', 0),
        'execution_time': execution_time,
        'rounds': len(result.get('rounds', [])),
        'solution_ready': result.get('is_solution_ready', False),
        'trace_json': result.get('trace_json', 'N/A'),
        'trace_txt': result.get('trace_txt', 'N/A')
    }
    
    print(f"\nFinal Answer: {metrics['final_answer']}")
    print(f"Correct: {metrics['correct']}")
    print(f"Total Tokens: {metrics['total_tokens']}")
    print(f"Execution Time: {metrics['execution_time']:.2f} seconds")
    print(f"Rounds: {metrics['rounds']}")
    
    return metrics


def run_bmas_test(problem, ground_truth, case_name, max_rounds=4):
    """Run case with bMAS (LbMAS - Paper style prompts)."""
    print("\n" + "="*80)
    print(f"RUNNING bMAS (Paper Prompts) - {case_name}")
    print("="*80)
    
    logger = ExperimentLogger(experiment_id=f"{case_name.lower().replace(' ', '_')}_bmas")
    
    start_time = time.time()
    result = run_bmas(
        problem=problem,
        max_rounds=max_rounds,
        ground_truth=ground_truth,
        enable_logging=True,
        logger=logger
    )
    execution_time = time.time() - start_time
    
    metrics = {
        'system': 'bMAS (Paper Prompts)',
        'case': case_name,
        'final_answer': result.get('final_answer', 'N/A'),
        'correct': result.get('correct', False),
        'total_tokens': result.get('total_tokens', 0),
        'execution_time': execution_time,
        'rounds': len(result.get('rounds', [])),
        'solution_ready': result.get('is_solution_ready', False),
        'trace_json': result.get('trace_json', 'N/A'),
        'trace_txt': result.get('trace_txt', 'N/A')
    }
    
    print(f"\nFinal Answer: {metrics['final_answer']}")
    print(f"Correct: {metrics['correct']}")
    print(f"Total Tokens: {metrics['total_tokens']}")
    print(f"Execution Time: {metrics['execution_time']:.2f} seconds")
    print(f"Rounds: {metrics['rounds']}")
    
    return metrics


def run_static_mas_test(problem, ground_truth, case_name):
    """Run case with Static MAS."""
    print("\n" + "="*80)
    print(f"RUNNING STATIC MAS - {case_name}")
    print("="*80)
    
    start_time = time.time()
    result = run_static_experiment(
        problem=problem,
        ground_truth=ground_truth,
        aggregation_method="majority_vote",
        enable_logging=True
    )
    execution_time = time.time() - start_time
    
    metrics = {
        'system': 'Static MAS',
        'case': case_name,
        'final_answer': result.get('final_answer', 'N/A'),
        'correct': result.get('correct', False),
        'total_tokens': result.get('total_tokens', 0),
        'execution_time': execution_time,
        'rounds': 1,
        'num_agents': len(result.get('agents', []))
    }
    
    print(f"\nFinal Answer: {metrics['final_answer']}")
    print(f"Correct: {metrics['correct']}")
    print(f"Total Tokens: {metrics['total_tokens']}")
    print(f"Execution Time: {metrics['execution_time']:.2f} seconds")
    
    return metrics


def run_cot_test(problem, ground_truth, case_name):
    """Run case with Chain-of-Thought baseline."""
    print("\n" + "="*80)
    print(f"RUNNING CHAIN-OF-THOUGHT BASELINE - {case_name}")
    print("="*80)
    
    start_time = time.time()
    result = run_cot_experiment(
        problem=problem,
        ground_truth=ground_truth,
        enable_logging=True
    )
    execution_time = time.time() - start_time
    
    metrics = {
        'system': 'Chain-of-Thought (CoT)',
        'case': case_name,
        'final_answer': result.get('final_answer', 'N/A'),
        'correct': result.get('correct', False),
        'total_tokens': result.get('tokens_used', 0),
        'execution_time': execution_time,
        'rounds': 1,
        'model_backend': result.get('model_backend', 'N/A')
    }
    
    print(f"\nFinal Answer: {metrics['final_answer']}")
    print(f"Correct: {metrics['correct']}")
    print(f"Total Tokens: {metrics['total_tokens']}")
    print(f"Execution Time: {metrics['execution_time']:.2f} seconds")
    
    return metrics


def compare_results(results, case_name, problem, ground_truth):
    """Compare results from all MAS setups for a specific case."""
    print("\n" + "="*80)
    print(f"COMPARISON RESULTS - {case_name}")
    print("="*80)
    print(f"\nProblem: {problem[:150]}...")
    print(f"Ground Truth: {ground_truth}\n")
    
    # Print comparison table
    print(f"{'System':<30} {'Answer':<20} {'Correct':<10} {'Tokens':<10} {'Time (s)':<12} {'Rounds':<10}")
    print("-" * 110)
    
    for result in results:
        answer_str = str(result['final_answer'])[:18]
        correct_str = "YES" if result['correct'] else "NO"
        rounds_str = str(result.get('rounds', 'N/A'))
        print(f"{result['system']:<30} {answer_str:<20} {correct_str:<10} {result['total_tokens']:<10} {result['execution_time']:<12.2f} {rounds_str:<10}")
    
    # Find best performers
    print("\n" + "="*80)
    print("PERFORMANCE ANALYSIS")
    print("="*80)
    
    # Accuracy
    correct_systems = [r['system'] for r in results if r['correct']]
    print(f"\nAccuracy:")
    print(f"  Correct: {', '.join(correct_systems) if correct_systems else 'None'}")
    print(f"  Incorrect: {', '.join([r['system'] for r in results if not r['correct']]) if any(not r['correct'] for r in results) else 'None'}")
    
    # Token efficiency
    if any(r['total_tokens'] > 0 for r in results):
        min_tokens = min(r['total_tokens'] for r in results if r['total_tokens'] > 0)
        most_efficient = [r['system'] for r in results if r['total_tokens'] == min_tokens]
        print(f"\nToken Efficiency (fewest tokens):")
        print(f"  Most Efficient: {', '.join(most_efficient)} ({min_tokens} tokens)")
        for r in results:
            if r['total_tokens'] != min_tokens and r['total_tokens'] > 0:
                diff = r['total_tokens'] - min_tokens
                pct = (diff / min_tokens) * 100
                print(f"  {r['system']}: {r['total_tokens']} tokens (+{diff}, +{pct:.1f}%)")
    
    # Speed
    min_time = min(r['execution_time'] for r in results)
    fastest = [r['system'] for r in results if r['execution_time'] == min_time]
    print(f"\nSpeed (fastest execution):")
    print(f"  Fastest: {', '.join(fastest)} ({min_time:.2f}s)")
    for r in results:
        if r['execution_time'] != min_time:
            diff = r['execution_time'] - min_time
            pct = (diff / min_time) * 100
            print(f"  {r['system']}: {r['execution_time']:.2f}s (+{diff:.2f}s, +{pct:.1f}%)")
    
    print("\n" + "="*80)


def run_case(case_data, is_hard=False):
    """Run a single case across all 4 MAS setups."""
    case_name = case_data["name"]
    problem = case_data["problem"]
    ground_truth = case_data["ground_truth"]
    max_rounds = 6 if is_hard else 4
    
    print("\n" + "="*80)
    print(f"RUNNING TEST CASE: {case_name}")
    print("="*80)
    print(f"\nProblem: {problem[:200]}...")
    print(f"Ground Truth: {ground_truth}")
    print("\nThis case will be run with:")
    print("  1. orig_impl_bMAS - Original Implementation Prompts")
    print("  2. bMAS (LbMAS) - Paper Style Prompts")
    print("  3. Static MAS - Parallel single-pass MAS")
    print("  4. Chain-of-Thought (CoT) - Baseline single-agent approach")
    print("="*80)
    
    all_results = []
    
    # Run each MAS setup
    try:
        result_orig_bmas = run_orig_bmas_test(problem, ground_truth, case_name, max_rounds)
        all_results.append(result_orig_bmas)
    except Exception as e:
        print(f"\nERROR running orig_impl_bMAS: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        result_bmas = run_bmas_test(problem, ground_truth, case_name, max_rounds)
        all_results.append(result_bmas)
    except Exception as e:
        print(f"\nERROR running bMAS: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        result_static = run_static_mas_test(problem, ground_truth, case_name)
        all_results.append(result_static)
    except Exception as e:
        print(f"\nERROR running Static MAS: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        result_cot = run_cot_test(problem, ground_truth, case_name)
        all_results.append(result_cot)
    except Exception as e:
        print(f"\nERROR running CoT: {e}")
        import traceback
        traceback.print_exc()
    
    # Compare results
    if all_results:
        compare_results(all_results, case_name, problem, ground_truth)
        
        print("\n" + "="*80)
        print(f"{case_name} - ALL TESTS COMPLETE")
        print("="*80)
        print("\nDetailed trace files are available in:")
        for result in all_results:
            if 'trace_txt' in result and result['trace_txt'] != 'N/A':
                print(f"  {result['system']}: {result['trace_txt']}")
        print("="*80)
    else:
        print(f"\nERROR: No results were collected for {case_name}. Check errors above.")
    
    return all_results


if __name__ == "__main__":
    print("\n" + "="*80)
    print("RUNNING ALL TEST CASES ACROSS ALL 4 MAS SETUPS")
    print("="*80)
    print("\nThis script will run:")
    print("  EASY CASES:")
    print("    Case A: Mathematical Problem (Drinkets to Trinkets)")
    print("    Case B: Common Knowledge Question (Why is the sky blue?)")
    print("\n  HARD CASES:")
    print("    Case C: Theoretical Physics (Maxwell's Equations)")
    print("    Case D: Astrophysics (Supermassive Black Hole Location)")
    print("\nEach case will be tested with:")
    print("  1. orig_impl_bMAS - Original Implementation Prompts")
    print("  2. bMAS (LbMAS) - Paper Style Prompts")
    print("  3. Static MAS - Parallel single-pass MAS")
    print("  4. Chain-of-Thought (CoT) - Baseline single-agent approach")
    print("\nResults will be compared at the end of each case.")
    print("="*80)
    
    all_case_results = {}
    
    # Run Easy Cases
    print("\n\n" + "#"*80)
    print("#"*80)
    print("STARTING EASY CASES")
    print("#"*80)
    print("#"*80)
    
    case_a_results = run_case(EASY_CASE_A, is_hard=False)
    all_case_results['Case A'] = case_a_results
    
    case_b_results = run_case(EASY_CASE_B, is_hard=False)
    all_case_results['Case B'] = case_b_results
    
    # Run Hard Cases
    print("\n\n" + "#"*80)
    print("#"*80)
    print("STARTING HARD CASES")
    print("#"*80)
    print("#"*80)
    
    case_c_results = run_case(HARD_CASE_C, is_hard=True)
    all_case_results['Case C'] = case_c_results
    
    case_d_results = run_case(HARD_CASE_D, is_hard=True)
    all_case_results['Case D'] = case_d_results
    
    # Final summary
    print("\n\n" + "="*80)
    print("FINAL SUMMARY - ALL CASES")
    print("="*80)
    
    for case_name, results in all_case_results.items():
        print(f"\n{case_name}:")
        correct_count = sum(1 for r in results if r.get('correct', False))
        total_count = len(results)
        print(f"  Systems that got correct answer: {correct_count}/{total_count}")
        expected_truth = EASY_CASE_A['ground_truth'] if 'Case A' in case_name else \
                        EASY_CASE_B['ground_truth'] if 'Case B' in case_name else \
                        HARD_CASE_C['ground_truth'] if 'Case C' in case_name else \
                        HARD_CASE_D['ground_truth']
        for r in results:
            status = "[CORRECT]" if r.get('correct', False) else "[INCORRECT]"
            print(f"    {status} {r['system']}: {r.get('final_answer', 'N/A')} (Expected: {expected_truth})")
    
    # Overall statistics
    print("\n" + "="*80)
    print("OVERALL STATISTICS")
    print("="*80)
    
    systems = ['orig_impl_bMAS (Original Prompts)', 'bMAS (Paper Prompts)', 'Static MAS', 'Chain-of-Thought (CoT)']
    for system in systems:
        correct = sum(1 for case_results in all_case_results.values() 
                     for r in case_results if r.get('system') == system and r.get('correct', False))
        total = sum(1 for case_results in all_case_results.values() 
                   for r in case_results if r.get('system') == system)
        accuracy = (correct / total * 100) if total > 0 else 0
        print(f"{system}: {correct}/{total} correct ({accuracy:.1f}%)")
    
    print("\n" + "="*80)
    print("ALL EXPERIMENTS COMPLETE")
    print("="*80)
    print("\nCheck individual case outputs above for detailed comparisons.")
    print("="*80)

