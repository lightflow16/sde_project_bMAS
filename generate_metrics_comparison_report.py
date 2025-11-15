"""
Generate a comprehensive comparison report showing all metrics for all 4 MAS systems.

This script scans the metrics_outputs directory for recent metrics files and generates
a side-by-side comparison report showing all 60 metrics across all systems.
"""
import json
import os
import glob
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict


# System name mappings
SYSTEM_NAMES = {
    "bMAS": "bMAS (LbMAS - Paper Prompts)",
    "orig_impl_bMAS": "orig_impl_bMAS (Original Prompts)",
    "Static_MAS": "Static MAS",
    "CoT": "Chain-of-Thought (CoT)"
}


def find_recent_metrics_files(metrics_dir: str = "metrics_outputs", 
                               max_files_per_system: int = 5) -> Dict[str, List[str]]:
    """
    Find recent metrics files for each system.
    
    Args:
        metrics_dir: Directory containing metrics files
        max_files_per_system: Maximum number of recent files per system
        
    Returns:
        Dictionary mapping system names to lists of file paths
    """
    if not os.path.exists(metrics_dir):
        print(f"Warning: Metrics directory '{metrics_dir}' does not exist.")
        return {}
    
    system_files = defaultdict(list)
    
    # Find all metrics JSON files
    pattern = os.path.join(metrics_dir, "*_metrics_*.json")
    all_files = glob.glob(pattern)
    
    # Group by system name
    for filepath in all_files:
        filename = os.path.basename(filepath)
        # Extract system name (everything before "_metrics_")
        if "_metrics_" in filename:
            system_name = filename.split("_metrics_")[0]
            system_files[system_name].append(filepath)
    
    # Sort by modification time (most recent first) and limit
    for system in system_files:
        system_files[system] = sorted(
            system_files[system],
            key=lambda x: os.path.getmtime(x),
            reverse=True
        )[:max_files_per_system]
    
    return dict(system_files)


def load_metrics(filepath: str) -> Optional[Dict[str, Any]]:
    """Load metrics from a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None


def format_value(value: Any, max_length: int = 50) -> str:
    """Format a metric value for display."""
    if value is None:
        return "N/A"
    elif isinstance(value, bool):
        return "Yes" if value else "No"
    elif isinstance(value, (int, float)):
        if isinstance(value, float):
            return f"{value:.2f}"
        return str(value)
    elif isinstance(value, list):
        if len(value) == 0:
            return "0"
        elif len(value) <= 3:
            return f"{len(value)} items"
        else:
            return f"{len(value)} items"
    elif isinstance(value, dict):
        if len(value) == 0:
            return "{}"
        return f"{len(value)} entries"
    elif isinstance(value, str):
        if len(value) > max_length:
            return value[:max_length-3] + "..."
        return value
    else:
        return str(value)[:max_length]


def generate_comparison_report(system_files: Dict[str, List[str]], 
                               output_file: str = "metrics_comparison_report.txt") -> str:
    """
    Generate a comprehensive comparison report.
    
    Args:
        system_files: Dictionary mapping system names to file paths
        output_file: Output file path
        
    Returns:
        Path to generated report file
    """
    # Load metrics for each system (use most recent file)
    system_metrics = {}
    system_info = {}
    
    for system_name, filepaths in system_files.items():
        if filepaths:
            # Use most recent file
            latest_file = filepaths[0]
            metrics = load_metrics(latest_file)
            if metrics:
                system_metrics[system_name] = metrics
                system_info[system_name] = {
                    "file": latest_file,
                    "timestamp": metrics.get("timestamp", "Unknown"),
                    "problem": metrics.get("problem", "N/A")[:100] if metrics.get("problem") else "N/A",
                    "final_answer": metrics.get("final_answer", "N/A"),
                    "correct": metrics.get("correct", "N/A")
                }
    
    if not system_metrics:
        print("No metrics files found to compare.")
        return None
    
    # Generate report
    report_lines = []
    report_lines.append("=" * 120)
    report_lines.append("COMPREHENSIVE METRICS COMPARISON REPORT - ALL 4 MAS SYSTEMS")
    report_lines.append("=" * 120)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    
    # System information
    report_lines.append("=" * 120)
    report_lines.append("SYSTEM INFORMATION")
    report_lines.append("=" * 120)
    for system_name, info in system_info.items():
        display_name = SYSTEM_NAMES.get(system_name, system_name)
        report_lines.append(f"\n{display_name}:")
        report_lines.append(f"  File: {info['file']}")
        report_lines.append(f"  Timestamp: {info['timestamp']}")
        report_lines.append(f"  Problem: {info['problem']}")
        report_lines.append(f"  Final Answer: {info['final_answer']}")
        report_lines.append(f"  Correct: {info['correct']}")
    report_lines.append("")
    
    # Category 1: Robustness
    report_lines.append("=" * 120)
    report_lines.append("1. ROBUSTNESS TO AGENT ERRORS AND OUTLIERS")
    report_lines.append("=" * 120)
    robustness_metrics = [
        ("Agent Errors", "robustness", "agent_errors", lambda x: len(x) if isinstance(x, list) else 0),
        ("Error Corrections", "robustness", "error_corrections"),
        ("Resilience Episodes", "robustness", "resilience_episodes"),
        ("Majority Vote Effectiveness", "robustness", "majority_vote_effectiveness"),
        ("Critique Recoveries", "robustness", "critique_recoveries"),
        ("Voting Recoveries", "robustness", "voting_recoveries"),
        ("Outlier Detections", "robustness", "outlier_detections"),
        ("Error Recovery Rate", "robustness", "error_recovery_rate"),
    ]
    generate_metric_table(report_lines, system_metrics, robustness_metrics)
    
    # Category 2: Consensus
    report_lines.append("")
    report_lines.append("=" * 120)
    report_lines.append("2. CONSENSUS AND DECISION QUALITY")
    report_lines.append("=" * 120)
    consensus_metrics = [
        ("Consensus Set Size", "consensus", "consensus_set_size"),
        ("Consensus Process", "consensus", "consensus_process"),
        ("Rounds to Consensus", "consensus", "rounds_to_consensus"),
        ("Critiques to Consensus", "consensus", "critiques_to_consensus"),
        ("Final Answer Agreement Rate", "consensus", "final_answer_agreement_rate"),
        ("Decision Confidence", "consensus", "decision_confidence"),
        ("Consensus History Entries", "consensus", "consensus_history", lambda x: len(x) if isinstance(x, list) else 0),
    ]
    generate_metric_table(report_lines, system_metrics, consensus_metrics)
    
    # Category 3: Explainability
    report_lines.append("")
    report_lines.append("=" * 120)
    report_lines.append("3. EXPLAINABILITY AND TRANSPARENCY")
    report_lines.append("=" * 120)
    explainability_metrics = [
        ("Reasoning Depth", "explainability", "reasoning_depth"),
        ("Trace Length (chars)", "explainability", "trace_length"),
        ("Trace Completeness", "explainability", "trace_completeness"),
        ("Agent Outputs Logged", "explainability", "agent_outputs_logged"),
        ("Decision Steps Logged", "explainability", "decision_steps_logged"),
        ("Critique Records", "explainability", "critique_records"),
        ("Clear Reasoning Path", "explainability", "clear_reasoning_path"),
        ("Trace Annotations", "explainability", "trace_annotations", lambda x: len(x) if isinstance(x, list) else 0),
    ]
    generate_metric_table(report_lines, system_metrics, explainability_metrics)
    
    # Category 4: Error Types
    report_lines.append("")
    report_lines.append("=" * 120)
    report_lines.append("4. ERROR TYPES AND FAILURE MODES")
    report_lines.append("=" * 120)
    error_metrics = [
        ("Wrong Math", "error_types", "wrong_math"),
        ("Answer Extraction Issues", "error_types", "answer_extraction_issues"),
        ("Parsing Errors", "error_types", "parsing_errors"),
        ("LLM Inconsistencies", "error_types", "llm_inconsistencies"),
        ("System Breakdowns", "error_types", "system_breakdowns"),
        ("Agent Failures", "error_types", "agent_failures", lambda x: len(x) if isinstance(x, list) else 0),
        ("Failure Modes", "error_types", "failure_modes", lambda x: len(x) if isinstance(x, list) else 0),
    ]
    generate_metric_table(report_lines, system_metrics, error_metrics)
    
    # Category 5: Resource Utilization
    report_lines.append("")
    report_lines.append("=" * 120)
    report_lines.append("5. RESOURCE UTILIZATION")
    report_lines.append("=" * 120)
    resource_metrics = [
        ("Total Tokens", "resources", "total_tokens"),
        ("Prompt Tokens", "resources", "prompt_tokens"),
        ("Completion Tokens", "resources", "completion_tokens"),
        ("Execution Time (s)", "resources", "execution_time"),
        ("Peak Memory (MB)", "resources", "peak_memory_mb"),
        ("Average CPU (%)", "resources", "average_cpu_percent"),
        ("Rounds", "resources", "rounds"),
        ("Agent Count", "resources", "agent_count"),
        ("LLM Calls", "resources", "llm_calls"),
    ]
    generate_metric_table(report_lines, system_metrics, resource_metrics)
    
    # Category 6: Quality Attributes
    report_lines.append("")
    report_lines.append("=" * 120)
    report_lines.append("6. QUALITY ATTRIBUTE TRACEABILITY")
    report_lines.append("=" * 120)
    quality_metrics = [
        ("Modularity Evidence", "quality_attributes", "modularity_evidence", lambda x: len(x) if isinstance(x, list) else 0),
        ("Scalability Evidence", "quality_attributes", "scalability_evidence", lambda x: len(x) if isinstance(x, list) else 0),
        ("Transparency Evidence", "quality_attributes", "transparency_evidence", lambda x: len(x) if isinstance(x, list) else 0),
        ("Reliability Evidence", "quality_attributes", "reliability_evidence", lambda x: len(x) if isinstance(x, list) else 0),
        ("Error Recovery Events", "quality_attributes", "error_recovery_events", lambda x: len(x) if isinstance(x, list) else 0),
        ("Traceable Critiques", "quality_attributes", "traceable_critiques", lambda x: len(x) if isinstance(x, list) else 0),
    ]
    generate_metric_table(report_lines, system_metrics, quality_metrics)
    
    # Category 7: User Experience
    report_lines.append("")
    report_lines.append("=" * 120)
    report_lines.append("7. USER/AUDITOR EXPERIENCE")
    report_lines.append("=" * 120)
    user_metrics = [
        ("Summary Log Quality", "user_experience", "summary_log_quality"),
        ("Side-by-Side Tables", "user_experience", "side_by_side_tables"),
        ("Correctness Reporting", "user_experience", "correctness_reporting"),
        ("Error Trace Quality", "user_experience", "error_trace_quality"),
        ("Reasonableness Check", "user_experience", "reasonableness_check"),
        ("Insight Clarity", "user_experience", "insight_clarity"),
        ("Audit Trail Completeness", "user_experience", "audit_trail_completeness"),
    ]
    generate_metric_table(report_lines, system_metrics, user_metrics)
    
    # Summary statistics
    report_lines.append("")
    report_lines.append("=" * 120)
    report_lines.append("SUMMARY STATISTICS")
    report_lines.append("=" * 120)
    
    # Find best performers
    if system_metrics:
        # Accuracy
        report_lines.append("\nAccuracy:")
        for system_name, metrics in system_metrics.items():
            correct = metrics.get("correct")
            display_name = SYSTEM_NAMES.get(system_name, system_name)
            if correct is True:
                report_lines.append(f"  ✓ {display_name}: CORRECT")
            elif correct is False:
                report_lines.append(f"  ✗ {display_name}: INCORRECT")
            else:
                report_lines.append(f"  ? {display_name}: Not evaluated")
        
        # Token efficiency
        report_lines.append("\nToken Efficiency (fewest tokens):")
        token_counts = {}
        for system_name, metrics in system_metrics.items():
            tokens = metrics.get("resources", {}).get("total_tokens", 0)
            if tokens > 0:
                token_counts[system_name] = tokens
        
        if token_counts:
            min_tokens = min(token_counts.values())
            for system_name, tokens in sorted(token_counts.items(), key=lambda x: x[1]):
                display_name = SYSTEM_NAMES.get(system_name, system_name)
                if tokens == min_tokens:
                    report_lines.append(f"  🏆 {display_name}: {tokens} tokens (BEST)")
                else:
                    diff = tokens - min_tokens
                    pct = (diff / min_tokens) * 100
                    report_lines.append(f"     {display_name}: {tokens} tokens (+{diff}, +{pct:.1f}%)")
        
        # Speed
        report_lines.append("\nSpeed (fastest execution):")
        time_counts = {}
        for system_name, metrics in system_metrics.items():
            time_val = metrics.get("resources", {}).get("execution_time", 0)
            if time_val > 0:
                time_counts[system_name] = time_val
        
        if time_counts:
            min_time = min(time_counts.values())
            for system_name, time_val in sorted(time_counts.items(), key=lambda x: x[1]):
                display_name = SYSTEM_NAMES.get(system_name, system_name)
                if time_val == min_time:
                    report_lines.append(f"  🏆 {display_name}: {time_val:.2f}s (BEST)")
                else:
                    diff = time_val - min_time
                    pct = (diff / min_time) * 100
                    report_lines.append(f"     {display_name}: {time_val:.2f}s (+{diff:.2f}s, +{pct:.1f}%)")
    
    report_lines.append("")
    report_lines.append("=" * 120)
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 120)
    
    # Write report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    return output_file


def generate_metric_table(report_lines: List[str], 
                          system_metrics: Dict[str, Dict[str, Any]],
                          metrics_list: List[tuple]):
    """Generate a table comparing a list of metrics across systems."""
    # Header
    header = f"{'Metric':<40}"
    for system_name in system_metrics.keys():
        display_name = SYSTEM_NAMES.get(system_name, system_name)
        # Truncate long names
        if len(display_name) > 25:
            display_name = display_name[:22] + "..."
        header += f" {display_name:<25}"
    report_lines.append(header)
    report_lines.append("-" * 120)
    
    # Rows
    for metric_info in metrics_list:
        metric_name = metric_info[0]
        category = metric_info[1]
        metric_key = metric_info[2]
        transform = metric_info[3] if len(metric_info) > 3 else None
        
        row = f"{metric_name:<40}"
        for system_name in system_metrics.keys():
            metrics = system_metrics[system_name]
            category_data = metrics.get(category, {})
            value = category_data.get(metric_key)
            
            if transform:
                value = transform(value)
            
            formatted_value = format_value(value, max_length=23)
            row += f" {formatted_value:<25}"
        
        report_lines.append(row)


def main():
    """Main function to generate comparison report."""
    print("Generating comprehensive metrics comparison report...")
    print("Scanning for metrics files...")
    
    # Find recent metrics files
    system_files = find_recent_metrics_files()
    
    if not system_files:
        print("No metrics files found. Please run some experiments first.")
        return
    
    print(f"Found metrics files for {len(system_files)} system(s):")
    for system_name, filepaths in system_files.items():
        display_name = SYSTEM_NAMES.get(system_name, system_name)
        print(f"  {display_name}: {len(filepaths)} file(s)")
        if filepaths:
            print(f"    Latest: {os.path.basename(filepaths[0])}")
    
    # Generate report
    output_file = generate_comparison_report(system_files)
    
    if output_file:
        print(f"\n✓ Comparison report generated: {output_file}")
        print(f"  Report includes all 60 metrics across all systems.")
    else:
        print("\n✗ Failed to generate report.")


if __name__ == "__main__":
    main()

