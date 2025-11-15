# Comprehensive Metrics Tracking Guide

## Overview

This document describes the comprehensive metrics tracking system that has been integrated into all 4 MAS (Multi-Agent System) implementations:

1. **bMAS** (LbMAS - Paper Style Prompts)
2. **orig_impl_bMAS** (Original Implementation Prompts)
3. **Static MAS** (Parallel single-pass MAS)
4. **Chain-of-Thought (CoT)** (Baseline single-agent approach)

## Metrics Categories

The metrics tracking system measures 7 comprehensive categories:

### 1. Robustness to Agent Errors and Outliers
- **Agent Errors**: Tracks all agent execution errors with details
- **Error Corrections**: Counts successful error recoveries
- **Resilience Episodes**: Number of times system recovered from errors
- **Majority Vote Effectiveness**: For Static MAS - measures voting success rate
- **Critique Recoveries**: For bMAS systems - critiques that led to corrections
- **Voting Recoveries**: For Static MAS - voting that corrected errors
- **Outlier Detections**: Counts of detected outlier agent outputs
- **Error Recovery Rate**: Calculated as recoveries / total_errors

### 2. Consensus and Decision Quality
- **Agents in Consensus**: List of agents contributing to final answer
- **Consensus Set Size**: Number of agents in consensus
- **Consensus Process**: Method used ("voting", "decider", "critic", "single_agent")
- **Rounds to Consensus**: Number of rounds needed (for iterative systems)
- **Critiques to Consensus**: Number of critiques needed (bMAS systems)
- **Final Answer Agreement Rate**: Proportion of agents agreeing
- **Decision Confidence**: Confidence score of final decision
- **Consensus History**: Complete history of consensus attempts

### 3. Explainability and Transparency
- **Reasoning Steps**: Complete list of reasoning steps with descriptions
- **Reasoning Depth**: Depth of reasoning chain
- **Trace Length**: Length of trace in characters
- **Trace Completeness**: Proportion of trace completeness
- **Agent Outputs Logged**: Number of agent outputs logged
- **Decision Steps Logged**: Number of decision steps logged
- **Critique Records**: Number of critique records (bMAS)
- **Clear Reasoning Path**: Boolean indicating if reasoning path is clear
- **Trace Annotations**: Annotated trace events

### 4. Error Types and Failure Modes
- **Wrong Math**: Count of wrong mathematical calculations
- **Answer Extraction Issues**: Issues extracting answer from output
- **Parsing Errors**: Parsing errors encountered
- **LLM Inconsistencies**: LLM inconsistencies detected
- **Agent Failures**: List of agent failure events with details
- **System Breakdowns**: Count of complete system breakdowns
- **Failure Modes**: Catalog of failure modes
- **Error Distribution**: Distribution of error types

### 5. Resource Utilization
- **Total Tokens**: Sum of all tokens used
- **Prompt Tokens**: Tokens used for prompts
- **Completion Tokens**: Tokens used for completions
- **Execution Time**: Total execution time in seconds
- **CPU Usage**: List of CPU usage samples
- **Memory Usage**: List of memory usage samples
- **Peak Memory**: Peak memory usage in MB
- **Average CPU Percent**: Average CPU usage percentage
- **Rounds**: Number of rounds (for iterative systems)
- **Agent Count**: Number of agents used
- **LLM Calls**: Number of LLM API calls
- **Resource per Correct Answer**: Calculated resource usage for correct answers
- **Resource per Incorrect Answer**: Calculated resource usage for incorrect answers

### 6. Quality Attribute Traceability
- **Modularity Evidence**: Evidence of modular design
- **Scalability Evidence**: Evidence of scalability
- **Transparency Evidence**: Evidence of transparency
- **Reliability Evidence**: Evidence of reliability
- **Error Recovery Events**: Error recovery events
- **Traceable Critiques**: Traceable critique events
- **Multi-System Comparison**: For comparison across systems

### 7. User/Auditor Experience
- **Summary Log Quality**: Quality score of summary log
- **Side-by-Side Tables**: Whether side-by-side tables exist
- **Correctness Reporting**: Quality of correctness reporting
- **Error Trace Quality**: Quality of error trace
- **Reasonableness Check**: Whether answer is reasonable
- **Insight Clarity**: Clarity of insights provided
- **Audit Trail Completeness**: Completeness of audit trail

## Usage

### Automatic Integration

Metrics tracking is **automatically enabled** in all experiment runners. No additional configuration is needed.

### Accessing Metrics

After running an experiment, metrics are automatically saved to:

1. **JSON File**: `metrics_outputs/{system_name}_metrics_{timestamp}.json`
2. **Summary Report**: `metrics_outputs/{system_name}_metrics_summary_{timestamp}.txt`

The experiment result dictionary also includes:
- `metrics_json`: Path to JSON metrics file
- `metrics_summary`: Path to summary report file

### Example Usage

```python
from bMAS.experiment_runner.run_experiment import run_single_experiment

result = run_single_experiment(
    problem="Your problem here",
    ground_truth="Expected answer",
    enable_logging=True
)

# Metrics are automatically tracked and saved
print(f"Metrics JSON: {result.get('metrics_json')}")
print(f"Metrics Summary: {result.get('metrics_summary')}")

# Access metrics directly from result
# (Note: Full metrics are in the JSON file)
```

### Reading Metrics

```python
import json

# Load metrics JSON
with open(result['metrics_json'], 'r') as f:
    metrics = json.load(f)

# Access specific metrics
robustness = metrics['robustness']
consensus = metrics['consensus']
explainability = metrics['explainability']
error_types = metrics['error_types']
resources = metrics['resources']
quality_attributes = metrics['quality_attributes']
user_experience = metrics['user_experience']

print(f"Error Recovery Rate: {robustness['error_recovery_rate']}")
print(f"Consensus Set Size: {consensus['consensus_set_size']}")
print(f"Reasoning Depth: {explainability['reasoning_depth']}")
print(f"Total Tokens: {resources['total_tokens']}")
```

## System-Specific Metrics

### bMAS / orig_impl_bMAS (Iterative Blackboard Systems)

**Unique Metrics:**
- **Critique Recoveries**: Tracks when critiques lead to corrections
- **Rounds to Consensus**: Number of iterative rounds needed
- **Blackboard Iterative Consensus**: Consensus through blackboard updates
- **Traceable Critiques**: Full critique records with round information

**Example Metrics:**
- Consensus process: "blackboard_iterative" or "decider_final"
- Rounds: 1-4 (configurable)
- Critiques to consensus: Number of critic interventions

### Static MAS (Parallel Single-Pass)

**Unique Metrics:**
- **Majority Vote Effectiveness**: Measures voting success rate
- **Voting Recoveries**: Errors corrected through voting
- **Parallel Execution**: All agents execute simultaneously

**Example Metrics:**
- Consensus process: "majority_vote", "decider_based", or "most_confident"
- Rounds: Always 1 (single-pass)
- Consensus set size: Number of agents agreeing with final answer

### CoT (Chain-of-Thought Baseline)

**Unique Metrics:**
- **Single Agent**: Only one agent (cot_agent)
- **Answer Extraction**: Tracks extraction success/failure
- **Reasoning Steps**: Step-by-step reasoning chain

**Example Metrics:**
- Consensus process: "single_agent"
- Rounds: Always 1 (single-pass)
- Agent count: Always 1

## Metrics Output Format

### JSON Structure

```json
{
  "system_name": "bMAS",
  "timestamp": "2024-01-01T12:00:00",
  "problem": "...",
  "ground_truth": "...",
  "final_answer": "...",
  "correct": true,
  "robustness": {
    "agent_errors": [...],
    "error_corrections": 2,
    "resilience_episodes": 2,
    "error_recovery_rate": 0.5
  },
  "consensus": {
    "agents_in_consensus": ["agent1", "agent2"],
    "consensus_set_size": 2,
    "consensus_process": "decider_final",
    "rounds_to_consensus": 2
  },
  "explainability": {
    "reasoning_steps": [...],
    "reasoning_depth": 15,
    "trace_length": 5000
  },
  "error_types": {
    "wrong_math": 0,
    "answer_extraction_issues": 1,
    "parsing_errors": 0,
    "llm_inconsistencies": 0
  },
  "resources": {
    "total_tokens": 5000,
    "execution_time": 45.2,
    "rounds": 2,
    "agent_count": 5
  },
  "quality_attributes": {
    "modularity_evidence": [...],
    "transparency_evidence": [...]
  },
  "user_experience": {
    "summary_log_quality": null,
    "side_by_side_tables": false
  }
}
```

### Summary Report Format

The summary report provides a human-readable text format with all key metrics organized by category.

## Comparison Across Systems

To compare metrics across all 4 systems, use the comparison scripts:

```bash
python run_all_cases_comparison.py
```

This will run all test cases across all systems and generate metrics for each. The metrics JSON files can then be compared programmatically.

## Advanced Usage

### Custom Metrics Tracker

You can create a custom metrics tracker instance:

```python
from metrics_tracker import MetricsTracker

tracker = MetricsTracker("custom_system")
tracker.start_tracking(problem, ground_truth)

# Add custom tracking
tracker.track_quality_attribute("reliability", "Custom evidence", "custom_event")

# Use in experiment
result = run_single_experiment(
    problem=problem,
    ground_truth=ground_truth,
    metrics_tracker=tracker
)
```

### Disabling Metrics

If you want to disable metrics tracking (not recommended), you can pass `None`:

```python
result = run_single_experiment(
    problem=problem,
    ground_truth=ground_truth,
    metrics_tracker=None  # Disables automatic creation
)
```

## Dependencies

The metrics tracker requires:
- `psutil` (optional, for CPU/memory tracking) - gracefully handles if not available
- Standard library: `json`, `os`, `time`, `datetime`, `typing`, `collections`

## Notes

- Metrics tracking adds minimal overhead to experiments
- All metrics are saved automatically - no manual intervention needed
- Metrics files are saved in `metrics_outputs/` directory
- The system gracefully handles missing dependencies (e.g., psutil)

## Future Enhancements

Potential enhancements:
- Comparative visualization across systems
- Automated metric analysis and reporting
- Integration with experiment management systems
- Real-time metrics dashboard
- Metric aggregation across multiple runs

