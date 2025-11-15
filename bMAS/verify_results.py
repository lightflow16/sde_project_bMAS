"""Quick script to verify LbMAS test results."""
import json
import os

print("="*80)
print("LbMAS TEST RESULTS VERIFICATION")
print("="*80)

# Check Case A
case_a_file = "bMAS/outputs/trace_case_a_mathematical.json"
if os.path.exists(case_a_file):
    with open(case_a_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("\nCase A: Mathematical Problem")
    print("-"*80)
    print(f"Final Answer: {data.get('final_answer', 'N/A')}")
    print(f"Ground Truth: {data.get('ground_truth', 'N/A')}")
    print(f"Correct: {data.get('final_answer', '').lower().strip() == data.get('ground_truth', '').lower().strip()}")
    print(f"Total Tokens: {data.get('total_tokens', 0)}")
    print(f"Rounds: {len(data.get('rounds', []))}")
    print(f"Solution Ready: {data.get('is_solution_ready', False)}")
    
    # Check for validation
    if 'decider_validated' in data:
        print(f"Validation Applied: {data.get('decider_validated', False)}")
        print(f"Validation Reason: {data.get('validation_reason', 'N/A')}")

# Check Case B
case_b_file = "bMAS/outputs/trace_case_b_common_knowledge.json"
if os.path.exists(case_b_file):
    with open(case_b_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("\nCase B: Common Knowledge Question")
    print("-"*80)
    print(f"Final Answer: {data.get('final_answer', 'N/A')}")
    print(f"Ground Truth: {data.get('ground_truth', 'N/A')}")
    
    # Check if answer contains ground truth
    final_answer = str(data.get('final_answer', '')).upper()
    ground_truth = str(data.get('ground_truth', '')).upper()
    correct = ground_truth in final_answer or final_answer.startswith(ground_truth)
    
    print(f"Correct: {correct}")
    print(f"Total Tokens: {data.get('total_tokens', 0)}")
    print(f"Rounds: {len(data.get('rounds', []))}")
    print(f"Solution Ready: {data.get('is_solution_ready', False)}")

print("\n" + "="*80)
print("VERIFICATION COMPLETE")
print("="*80)

