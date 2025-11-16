"""
Convert existing experiment runs to metrics format and generate comparison reports.

This script scans existing trace/log files from past runs and converts them to
the comprehensive metrics format, then generates comparison reports.
"""
import json
import os
import glob
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Import metrics tracker to use its structure
try:
    from metrics_tracker import MetricsTracker
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    print("Warning: metrics_tracker not available. Creating basic metrics structure.")


def convert_bmas_trace(trace_file: str) -> Optional[Dict[str, Any]]:
    """Convert bMAS trace file to metrics format."""
    try:
        with open(trace_file, 'r', encoding='utf-8') as f:
            trace = json.load(f)
        
        # Create metrics structure
        metrics = create_base_metrics("bMAS")
        metrics["problem"] = trace.get("problem", "")
        metrics["ground_truth"] = trace.get("ground_truth", "")
        metrics["final_answer"] = trace.get("final_answer", "")
        
        # Calculate correctness if ground truth exists
        if trace.get("ground_truth") and trace.get("final_answer"):
            metrics["correct"] = evaluate_answer_simple(
                trace.get("final_answer", ""),
                trace.get("ground_truth", "")
            )
        
        # Extract from trace
        rounds = trace.get("rounds", [])
        agent_pool = trace.get("agent_pool", [])
        
        # Resources
        metrics["resources"]["total_tokens"] = trace.get("total_tokens", 0)
        metrics["resources"]["rounds"] = len(rounds)
        metrics["resources"]["agent_count"] = len(agent_pool)
        
        # Calculate execution time
        start_time = trace.get("start_time", "")
        end_time = trace.get("end_time", "")
        if start_time and end_time:
            try:
                start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                metrics["resources"]["execution_time"] = (end - start).total_seconds()
            except:
                pass
        
        # Consensus
        consensus_agents = []
        for round_data in rounds:
            for output in round_data.get("agent_outputs", []):
                agent_name = output.get("agent", "")
                if agent_name and agent_name not in consensus_agents:
                    consensus_agents.append(agent_name)
        
        metrics["consensus"]["agents_in_consensus"] = consensus_agents
        metrics["consensus"]["consensus_set_size"] = len(consensus_agents)
        metrics["consensus"]["rounds_to_consensus"] = len(rounds)
        metrics["consensus"]["consensus_process"] = "blackboard_iterative"
        
        # Explainability
        reasoning_steps = []
        for round_data in rounds:
            for output in round_data.get("agent_outputs", []):
                agent_name = output.get("agent", "")
                response_type = output.get("response_type", "unknown")
                reasoning_steps.append({
                    "description": f"Round {round_data.get('round', 0)}: {agent_name} produced {response_type}",
                    "agent": agent_name,
                    "type": "agent_action",
                    "timestamp": trace.get("start_time", "")
                })
        
        metrics["explainability"]["reasoning_steps"] = reasoning_steps
        metrics["explainability"]["reasoning_depth"] = len(reasoning_steps)
        metrics["explainability"]["agent_outputs_logged"] = len(reasoning_steps)
        
        # Count critiques
        critique_count = 0
        for round_data in rounds:
            for output in round_data.get("agent_outputs", []):
                if output.get("agent") == "critic":
                    critique_count += 1
        
        metrics["explainability"]["critique_records"] = critique_count
        metrics["consensus"]["critiques_to_consensus"] = critique_count
        
        # Quality attributes
        metrics["quality_attributes"]["modularity_evidence"].append({
            "evidence": f"Agent pool with {len(agent_pool)} agents (predefined + generated)",
            "type": "architecture",
            "timestamp": trace.get("start_time", "")
        })
        metrics["quality_attributes"]["transparency_evidence"].append({
            "evidence": "Full blackboard trace with agent actions",
            "type": "logging",
            "timestamp": trace.get("start_time", "")
        })
        
        return metrics
    except Exception as e:
        print(f"Error converting bMAS trace {trace_file}: {e}")
        return None


def convert_static_mas_trace(trace_file: str) -> Optional[Dict[str, Any]]:
    """Convert Static MAS trace file to metrics format."""
    try:
        with open(trace_file, 'r', encoding='utf-8') as f:
            trace = json.load(f)
        
        metrics = create_base_metrics("Static_MAS")
        metrics["problem"] = trace.get("problem", "")
        metrics["ground_truth"] = trace.get("ground_truth", "")
        
        aggregation = trace.get("aggregation", {})
        metrics["final_answer"] = aggregation.get("final_answer", trace.get("final_answer", ""))
        
        # Calculate correctness
        if trace.get("ground_truth") and metrics["final_answer"]:
            metrics["correct"] = evaluate_answer_simple(
                metrics["final_answer"],
                trace.get("ground_truth", "")
            )
        
        # Resources
        metrics["resources"]["total_tokens"] = trace.get("total_tokens", 0)
        metrics["resources"]["rounds"] = 1  # Static MAS is single-pass
        metrics["resources"]["agent_count"] = len(trace.get("agents", []))
        metrics["resources"]["execution_time"] = trace.get("execution_time", 0)
        
        # Agent results
        agent_results = trace.get("agent_results", [])
        
        # Consensus
        contributing_agents = []
        final_answer = str(metrics["final_answer"]) if metrics["final_answer"] else ""
        aggregation_method = trace.get("aggregation_method", "majority_vote")
        
        for result in agent_results:
            agent_answer = str(result.get("answer", ""))
            if agent_answer.strip().lower() == final_answer.strip().lower():
                contributing_agents.append(result.get("agent", ""))
        
        metrics["consensus"]["agents_in_consensus"] = contributing_agents
        metrics["consensus"]["consensus_set_size"] = len(contributing_agents)
        metrics["consensus"]["rounds_to_consensus"] = 1
        metrics["consensus"]["consensus_process"] = aggregation_method
        
        if aggregation_method == "majority_vote" and len(agent_results) > 0:
            metrics["robustness"]["majority_vote_effectiveness"] = len(contributing_agents) / len(agent_results)
        
        # Explainability
        reasoning_steps = []
        for result in agent_results:
            agent_name = result.get("agent", "")
            answer = result.get("answer", "")
            reasoning_steps.append({
                "description": f"Agent {agent_name} produced answer: {answer[:100]}",
                "agent": agent_name,
                "type": "agent_action",
                "timestamp": trace.get("timestamp", "")
            })
        
        metrics["explainability"]["reasoning_steps"] = reasoning_steps
        metrics["explainability"]["reasoning_depth"] = len(reasoning_steps)
        metrics["explainability"]["agent_outputs_logged"] = len(agent_results)
        
        # Track errors
        error_count = 0
        for result in agent_results:
            if result.get("error"):
                error_count += 1
                metrics["robustness"]["agent_errors"].append({
                    "agent": result.get("agent", ""),
                    "error_type": "execution_error",
                    "error_message": result.get("error", ""),
                    "timestamp": trace.get("timestamp", "")
                })
        
        # Quality attributes
        metrics["quality_attributes"]["modularity_evidence"].append({
            "evidence": f"Fixed-role agents with parallel execution ({len(trace.get('agents', []))} agents)",
            "type": "architecture",
            "timestamp": trace.get("timestamp", "")
        })
        metrics["quality_attributes"]["scalability_evidence"].append({
            "evidence": "Parallel execution with ThreadPoolExecutor",
            "type": "execution",
            "timestamp": trace.get("timestamp", "")
        })
        
        return metrics
    except Exception as e:
        print(f"Error converting Static MAS trace {trace_file}: {e}")
        return None


def convert_cot_trace(trace_file: str) -> Optional[Dict[str, Any]]:
    """Convert CoT trace file to metrics format."""
    try:
        with open(trace_file, 'r', encoding='utf-8') as f:
            trace = json.load(f)
        
        metrics = create_base_metrics("CoT")
        metrics["problem"] = trace.get("problem", "")
        metrics["ground_truth"] = trace.get("ground_truth", "")
        metrics["final_answer"] = trace.get("final_answer", "")
        
        # Calculate correctness
        if trace.get("ground_truth") and metrics["final_answer"]:
            metrics["correct"] = evaluate_answer_simple(
                metrics["final_answer"],
                trace.get("ground_truth", "")
            )
        
        # Resources
        metrics["resources"]["total_tokens"] = trace.get("tokens_used", 0)
        metrics["resources"]["prompt_tokens"] = trace.get("prompt_tokens", 0)
        metrics["resources"]["completion_tokens"] = trace.get("completion_tokens", 0)
        metrics["resources"]["rounds"] = 1
        metrics["resources"]["agent_count"] = 1
        metrics["resources"]["execution_time"] = trace.get("execution_time", 0)
        metrics["resources"]["llm_calls"] = 1
        
        # Consensus
        metrics["consensus"]["agents_in_consensus"] = ["cot_agent"]
        metrics["consensus"]["consensus_set_size"] = 1
        metrics["consensus"]["rounds_to_consensus"] = 1
        metrics["consensus"]["consensus_process"] = "single_agent"
        
        # Explainability
        reasoning = trace.get("reasoning", "")
        if reasoning:
            metrics["explainability"]["reasoning_steps"] = [{
                "description": f"CoT reasoning: {reasoning[:500]}",
                "agent": "cot_agent",
                "type": "reasoning",
                "timestamp": trace.get("timestamp", "")
            }]
            metrics["explainability"]["reasoning_depth"] = 1
            metrics["explainability"]["trace_length"] = len(reasoning)
            metrics["explainability"]["agent_outputs_logged"] = 1
        
        # Check for extraction issues
        if metrics["final_answer"] in ["No answer found", ""] or len(metrics["final_answer"]) < 2:
            metrics["error_types"]["answer_extraction_issues"] = 1
        
        # Quality attributes
        metrics["quality_attributes"]["transparency_evidence"].append({
            "evidence": "Single-agent CoT with step-by-step reasoning",
            "type": "architecture",
            "timestamp": trace.get("timestamp", "")
        })
        
        return metrics
    except Exception as e:
        print(f"Error converting CoT trace {trace_file}: {e}")
        return None


def create_base_metrics(system_name: str) -> Dict[str, Any]:
    """Create base metrics structure."""
    return {
        "system_name": system_name,
        "timestamp": datetime.now().isoformat(),
        "problem": None,
        "ground_truth": None,
        "final_answer": None,
        "correct": None,
        "robustness": {
            "agent_errors": [],
            "error_corrections": 0,
            "resilience_episodes": 0,
            "majority_vote_effectiveness": None,
            "critique_recoveries": 0,
            "voting_recoveries": 0,
            "outlier_detections": 0,
            "error_recovery_rate": None
        },
        "consensus": {
            "agents_in_consensus": [],
            "consensus_set_size": 0,
            "consensus_process": None,
            "rounds_to_consensus": 0,
            "critiques_to_consensus": 0,
            "final_answer_agreement_rate": None,
            "decision_confidence": None,
            "consensus_history": []
        },
        "explainability": {
            "reasoning_steps": [],
            "reasoning_depth": 0,
            "trace_length": 0,
            "trace_completeness": None,
            "agent_outputs_logged": 0,
            "decision_steps_logged": 0,
            "critique_records": 0,
            "clear_reasoning_path": False,
            "trace_annotations": []
        },
        "error_types": {
            "wrong_math": 0,
            "answer_extraction_issues": 0,
            "parsing_errors": 0,
            "llm_inconsistencies": 0,
            "agent_failures": [],
            "system_breakdowns": 0,
            "failure_modes": [],
            "error_distribution": {}
        },
        "resources": {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "execution_time": 0.0,
            "cpu_usage": [],
            "memory_usage": [],
            "peak_memory_mb": 0,
            "average_cpu_percent": 0.0,
            "rounds": 0,
            "agent_count": 0,
            "llm_calls": 0,
            "resource_per_correct_answer": None,
            "resource_per_incorrect_answer": None
        },
        "quality_attributes": {
            "modularity_evidence": [],
            "scalability_evidence": [],
            "transparency_evidence": [],
            "reliability_evidence": [],
            "error_recovery_events": [],
            "traceable_critiques": [],
            "multi_system_comparison": {}
        },
        "user_experience": {
            "summary_log_quality": None,
            "side_by_side_tables": False,
            "correctness_reporting": None,
            "error_trace_quality": None,
            "reasonableness_check": None,
            "insight_clarity": None,
            "audit_trail_completeness": None
        }
    }


def evaluate_answer_simple(predicted: str, ground_truth: str) -> bool:
    """Simple answer evaluation."""
    pred_norm = str(predicted).lower().strip()
    gt_norm = str(ground_truth).lower().strip()
    
    if pred_norm == gt_norm:
        return True
    
    if gt_norm in pred_norm:
        return True
    
    import re
    pred_numbers = re.findall(r'\d+\.?\d*', pred_norm)
    gt_numbers = re.findall(r'\d+\.?\d*', gt_norm)
    
    if pred_numbers and gt_numbers:
        return pred_numbers[-1] == gt_numbers[-1]
    
    # Extract letters for multiple choice
    pred_chars = re.findall(r'[A-Z]', pred_norm.upper())
    gt_chars = re.findall(r'[A-Z]', gt_norm.upper())
    if pred_chars and gt_chars:
        return pred_chars[-1] == gt_chars[-1]
    
    return False


def find_and_convert_traces():
    """Find all trace files and convert them to metrics."""
    os.makedirs("metrics_outputs", exist_ok=True)
    
    converted_count = 0
    
    # bMAS traces
    print("Scanning for bMAS traces...")
    bmas_patterns = [
        "bMAS/outputs/trace_*.json",
        "bMAS/outputs/*trace*.json"
    ]
    for pattern in bmas_patterns:
        for trace_file in glob.glob(pattern):
            print(f"  Converting: {trace_file}")
            metrics = convert_bmas_trace(trace_file)
            if metrics:
                # Extract timestamp from filename or use current
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                if "case_" in trace_file:
                    # Try to extract case name
                    case_name = os.path.basename(trace_file).replace("trace_", "").replace(".json", "")
                    timestamp = f"{case_name}_{timestamp}"
                
                output_file = f"metrics_outputs/bMAS_metrics_{timestamp}.json"
                with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
                    json.dump(metrics, f, indent=2)
                print(f"    Saved: {output_file}")
                converted_count += 1
    
    # Static MAS traces
    print("\nScanning for Static MAS traces...")
    static_patterns = [
        "static_mas/outputs/static_mas_trace_*.json"
    ]
    for pattern in static_patterns:
        for trace_file in glob.glob(pattern):
            print(f"  Converting: {trace_file}")
            metrics = convert_static_mas_trace(trace_file)
            if metrics:
                # Extract timestamp from filename
                filename = os.path.basename(trace_file)
                if "static_mas_trace_" in filename:
                    timestamp = filename.replace("static_mas_trace_", "").replace(".json", "")
                else:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                output_file = f"metrics_outputs/Static_MAS_metrics_{timestamp}.json"
                with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
                    json.dump(metrics, f, indent=2)
                print(f"    Saved: {output_file}")
                converted_count += 1
    
    # CoT traces
    print("\nScanning for CoT traces...")
    cot_patterns = [
        "cot/outputs/cot_trace_*.json"
    ]
    for pattern in cot_patterns:
        for trace_file in glob.glob(pattern):
            print(f"  Converting: {trace_file}")
            metrics = convert_cot_trace(trace_file)
            if metrics:
                # Extract timestamp from filename
                filename = os.path.basename(trace_file)
                if "cot_trace_" in filename:
                    timestamp = filename.replace("cot_trace_", "").replace(".json", "")
                else:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                output_file = f"metrics_outputs/CoT_metrics_{timestamp}.json"
                with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
                    json.dump(metrics, f, indent=2)
                print(f"    Saved: {output_file}")
                converted_count += 1
    
    # orig_impl_bMAS traces (if they exist)
    print("\nScanning for orig_impl_bMAS traces...")
    orig_patterns = [
        "orig_impl_bMAS/outputs/trace_*.json",
        "orig_impl_bMAS/outputs/*trace*.json"
    ]
    for pattern in orig_patterns:
        for trace_file in glob.glob(pattern):
            print(f"  Converting: {trace_file}")
            metrics = convert_bmas_trace(trace_file)  # Same format as bMAS
            if metrics:
                metrics["system_name"] = "orig_impl_bMAS"
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"metrics_outputs/orig_impl_bMAS_metrics_{timestamp}.json"
                with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
                    json.dump(metrics, f, indent=2)
                print(f"    Saved: {output_file}")
                converted_count += 1
    
    print(f"\n[SUCCESS] Converted {converted_count} trace files to metrics format")
    return converted_count


def main():
    """Main function."""
    print("=" * 80)
    print("CONVERTING EXISTING RUNS TO METRICS FORMAT")
    print("=" * 80)
    print()
    
    converted = find_and_convert_traces()
    
    if converted > 0:
        print("\n" + "=" * 80)
        print("GENERATING COMPARISON REPORT")
        print("=" * 80)
        
        # Now generate comparison report
        try:
            from generate_metrics_comparison_report import generate_comparison_report, find_recent_metrics_files
            
            system_files = find_recent_metrics_files()
            if system_files:
                report_path = generate_comparison_report(system_files, "metrics_comparison_report_from_existing_runs.txt")
                print(f"\n[SUCCESS] Comparison report generated: {report_path}")
            else:
                print("\n⚠ No metrics files found for comparison")
        except Exception as e:
            print(f"\n⚠ Could not generate comparison report: {e}")
            print("   You can run: python generate_metrics_comparison_report.py")
    else:
        print("\n⚠ No trace files found to convert")
        print("   Make sure trace files exist in:")
        print("   - bMAS/outputs/")
        print("   - static_mas/outputs/")
        print("   - cot/outputs/")
        print("   - orig_impl_bMAS/outputs/")


if __name__ == "__main__":
    main()

