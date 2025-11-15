"""
Compare Static MAS results with LbMAS results for the same test cases.
"""
import json
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_lbmas_result(case_name):
    """Load LbMAS result from trace JSON file."""
    trace_file = f"outputs/trace_case_{case_name}.json"
    if os.path.exists(trace_file):
        with open(trace_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def load_static_mas_result(case_name):
    """Load Static MAS result from trace JSON file."""
    # Find the most recent trace file
    output_dir = Path("static_mas/outputs")
    if not output_dir.exists():
        return None
    
    # Look for trace files matching the case
    trace_files = list(output_dir.glob("static_mas_trace_*.json"))
    if not trace_files:
        return None
    
    # Get the most recent one (or we could search by timestamp)
    # For now, let's check the last few files
    trace_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    # Try to find one that matches our case (we'll need to check content)
    for trace_file in trace_files[:5]:  # Check last 5 files
        try:
            with open(trace_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Check if this matches our case by looking at problem
                problem = data.get('problem', '')
                if case_name == 'a_mathematical' and 'Trinket' in problem:
                    return data
                elif case_name == 'b_common_knowledge' and 'sky blue' in problem:
                    return data
        except Exception as e:
            continue
    
    return None


def extract_metrics(result, system_name):
    """Extract key metrics from result."""
    if result is None:
        return None
    
    metrics = {
        'system': system_name,
        'final_answer': result.get('final_answer', 'N/A'),
        'total_tokens': result.get('total_tokens', 0),
    }
    
    if system_name == 'LbMAS':
        # Calculate execution time from start_time and end_time
        from datetime import datetime
        start_time = result.get('start_time', '')
        end_time = result.get('end_time', '')
        if start_time and end_time:
            try:
                start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                metrics['execution_time'] = (end - start).total_seconds()
            except:
                metrics['execution_time'] = 0
        else:
            metrics['execution_time'] = 0
        
        # Check correctness - use evaluate_answer function if available
        ground_truth = result.get('ground_truth', '')
        final_answer = str(result.get('final_answer', ''))
        
        # Simple evaluation
        pred_norm = final_answer.lower().strip()
        gt_norm = ground_truth.lower().strip()
        
        # Exact match or contains ground truth
        if pred_norm == gt_norm:
            metrics['correct'] = True
        elif gt_norm in pred_norm:
            metrics['correct'] = True
        else:
            # Extract numbers/letters for comparison
            import re
            pred_chars = re.findall(r'[A-Z]', pred_norm.upper())
            gt_chars = re.findall(r'[A-Z]', gt_norm.upper())
            if pred_chars and gt_chars:
                metrics['correct'] = (pred_chars[-1] == gt_chars[-1])
            else:
                metrics['correct'] = False
        
        metrics['rounds'] = len(result.get('rounds', []))
        metrics['is_solution_ready'] = result.get('is_solution_ready', False)
        # Count agents
        agent_pool = result.get('agent_pool', [])
        if isinstance(agent_pool, list):
            metrics['num_agents'] = len(agent_pool)
        else:
            metrics['num_agents'] = 'N/A'
    elif system_name == 'Static MAS':
        metrics['execution_time'] = result.get('execution_time', 0)
        # Use the correct value from the result if available, otherwise calculate
        if 'correct' in result:
            metrics['correct'] = result.get('correct', False)
        else:
            # Calculate correctness
            ground_truth = result.get('ground_truth', '')
            final_answer = str(result.get('final_answer', ''))
            pred_norm = final_answer.lower().strip()
            gt_norm = ground_truth.lower().strip()
            
            if pred_norm == gt_norm:
                metrics['correct'] = True
            elif gt_norm in pred_norm:
                metrics['correct'] = True
            else:
                # Extract letters for multiple choice questions
                import re
                pred_chars = re.findall(r'[A-Z]', pred_norm.upper())
                gt_chars = re.findall(r'[A-Z]', gt_norm.upper())
                if pred_chars and gt_chars:
                    metrics['correct'] = (pred_chars[-1] == gt_chars[-1])
                else:
                    metrics['correct'] = False
        
        metrics['num_agents'] = len(result.get('agents', []))
        metrics['aggregation_method'] = result.get('aggregation_method', 'N/A')
        metrics['rounds'] = 1  # Static MAS is single-pass
    
    return metrics


def compare_results():
    """Compare LbMAS and Static MAS results."""
    print("="*80)
    print("COMPARISON: LbMAS vs Static MAS")
    print("="*80)
    
    cases = [
        ('a_mathematical', 'Case A: Mathematical Problem'),
        ('b_common_knowledge', 'Case B: Common Knowledge Question')
    ]
    
    all_comparisons = []
    
    for case_id, case_name in cases:
        print(f"\n{'='*80}")
        print(case_name)
        print('='*80)
        
        # Load results
        lbmas_result = load_lbmas_result(case_id)
        static_mas_result = load_static_mas_result(case_id)
        
        if lbmas_result:
            lbmas_metrics = extract_metrics(lbmas_result, 'LbMAS')
        else:
            print(f"[WARNING] LbMAS result not found for {case_name}")
            lbmas_metrics = None
        
        if static_mas_result:
            static_mas_metrics = extract_metrics(static_mas_result, 'Static MAS')
        else:
            print(f"[WARNING] Static MAS result not found for {case_name}")
            static_mas_metrics = None
        
        # Print comparison
        if lbmas_metrics and static_mas_metrics:
            print(f"\nProblem: {lbmas_result.get('problem', 'N/A')[:80]}...")
            print(f"Ground Truth: {lbmas_result.get('ground_truth', 'N/A')}")
            
            print(f"\n{'Metric':<30} {'LbMAS':<25} {'Static MAS':<25}")
            print('-'*80)
            
            for key in ['final_answer', 'correct', 'total_tokens', 'execution_time', 'num_agents', 'rounds']:
                lbmas_val = lbmas_metrics.get(key, 'N/A')
                static_val = static_mas_metrics.get(key, 'N/A')
                
                # Format values
                if key == 'execution_time':
                    lbmas_val = f"{lbmas_val:.2f}s" if isinstance(lbmas_val, (int, float)) else lbmas_val
                    static_val = f"{static_val:.2f}s" if isinstance(static_val, (int, float)) else static_val
                elif key == 'correct':
                    lbmas_val = "[OK]" if lbmas_val else "[X]"
                    static_val = "[OK]" if static_val else "[X]"
                
                print(f"{key:<30} {str(lbmas_val):<25} {str(static_val):<25}")
            
            if 'aggregation_method' in static_mas_metrics:
                print(f"{'aggregation_method':<30} {'N/A (iterative)':<25} {static_mas_metrics['aggregation_method']:<25}")
            
            # Calculate differences
            print(f"\nDifferences:")
            token_diff = static_mas_metrics['total_tokens'] - lbmas_metrics['total_tokens']
            token_pct = (token_diff / lbmas_metrics['total_tokens'] * 100) if lbmas_metrics['total_tokens'] > 0 else 0
            print(f"  Token difference: {token_diff:+d} ({token_pct:+.1f}%)")
            
            time_diff = static_mas_metrics['execution_time'] - lbmas_metrics['execution_time']
            time_pct = (time_diff / lbmas_metrics['execution_time'] * 100) if lbmas_metrics['execution_time'] > 0 else 0
            print(f"  Time difference: {time_diff:+.2f}s ({time_pct:+.1f}%)")
            
            all_comparisons.append({
                'case': case_name,
                'lbmas': lbmas_metrics,
                'static_mas': static_mas_metrics
            })
        else:
            print(f"[ERROR] Could not load results for comparison")
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print('='*80)
    
    if all_comparisons:
        total_lbmas_tokens = sum(c['lbmas']['total_tokens'] for c in all_comparisons)
        total_static_tokens = sum(c['static_mas']['total_tokens'] for c in all_comparisons)
        total_lbmas_time = sum(c['lbmas']['execution_time'] for c in all_comparisons)
        total_static_time = sum(c['static_mas']['execution_time'] for c in all_comparisons)
        
        lbmas_correct = sum(1 for c in all_comparisons if c['lbmas']['correct'])
        static_correct = sum(1 for c in all_comparisons if c['static_mas']['correct'])
        
        print(f"\nTotal Tokens:")
        print(f"  LbMAS: {total_lbmas_tokens}")
        print(f"  Static MAS: {total_static_tokens}")
        print(f"  Difference: {total_static_tokens - total_lbmas_tokens:+d} ({(total_static_tokens - total_lbmas_tokens) / total_lbmas_tokens * 100:+.1f}%)")
        
        print(f"\nTotal Execution Time:")
        print(f"  LbMAS: {total_lbmas_time:.2f}s")
        print(f"  Static MAS: {total_static_time:.2f}s")
        print(f"  Difference: {total_static_time - total_lbmas_time:+.2f}s ({(total_static_time - total_lbmas_time) / total_lbmas_time * 100:+.1f}%)")
        
        print(f"\nAccuracy:")
        print(f"  LbMAS: {lbmas_correct}/{len(all_comparisons)} ({lbmas_correct/len(all_comparisons)*100:.0f}%)")
        print(f"  Static MAS: {static_correct}/{len(all_comparisons)} ({static_correct/len(all_comparisons)*100:.0f}%)")
        
        print(f"\nKey Observations:")
        print(f"  - Static MAS uses {'more' if total_static_tokens > total_lbmas_tokens else 'fewer'} tokens")
        print(f"  - Static MAS is {'slower' if total_static_time > total_lbmas_time else 'faster'}")
        print(f"  - Both systems achieved {'the same' if lbmas_correct == static_correct else 'different'} accuracy")
        print(f"  - LbMAS uses iterative rounds, Static MAS uses single parallel pass")
    
    print('='*80)


if __name__ == "__main__":
    compare_results()

