"""
Comprehensive Metrics Tracker for Multi-Agent Systems.

Tracks all metrics across 7 categories:
1. Robustness to Agent Errors and Outliers
2. Consensus and Decision Quality
3. Explainability and Transparency
4. Error Types and Failure Modes
5. Resource Utilization
6. Quality Attribute Traceability
7. User/Auditor Experience
"""
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Set
from collections import defaultdict

# Try to import psutil, but handle gracefully if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class MetricsTracker:
    """Comprehensive metrics tracker for MAS systems."""
    
    def __init__(self, system_name: str, output_dir: str = "metrics_outputs"):
        """Initialize metrics tracker."""
        self.system_name = system_name
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Track process for resource monitoring
        if PSUTIL_AVAILABLE:
            try:
                self.process = psutil.Process()
            except Exception:
                self.process = None
        else:
            self.process = None
        self.start_time = None
        self.start_memory = None
        
        # Initialize all metric categories
        self.metrics = {
            "system_name": system_name,
            "timestamp": datetime.now().isoformat(),
            "problem": None,
            "ground_truth": None,
            
            # 1. Robustness to Agent Errors and Outliers
            "robustness": {
                "agent_errors": [],  # List of agent errors encountered
                "error_corrections": 0,  # Count of answer corrections
                "resilience_episodes": 0,  # Count of recovery episodes
                "majority_vote_effectiveness": None,  # For Static MAS
                "critique_recoveries": 0,  # For bMAS - critiques that led to corrections
                "voting_recoveries": 0,  # For Static MAS - voting that corrected errors
                "outlier_detections": 0,  # Count of detected outliers
                "error_recovery_rate": None  # Calculated: recoveries / total_errors
            },
            
            # 2. Consensus and Decision Quality
            "consensus": {
                "agents_in_consensus": [],  # List of agents contributing to final answer
                "consensus_set_size": 0,  # Number of agents in consensus
                "consensus_process": None,  # "voting", "decider", "critic", "single_agent"
                "rounds_to_consensus": 0,  # Number of rounds needed
                "critiques_to_consensus": 0,  # Number of critiques needed (bMAS)
                "final_answer_agreement_rate": None,  # Proportion of agents agreeing
                "decision_confidence": None,  # Confidence score of final decision
                "consensus_history": []  # History of consensus attempts
            },
            
            # 3. Explainability and Transparency
            "explainability": {
                "reasoning_steps": [],  # List of reasoning steps
                "reasoning_depth": 0,  # Depth of reasoning chain
                "trace_length": 0,  # Length of trace in characters
                "trace_completeness": None,  # Proportion of trace completeness
                "agent_outputs_logged": 0,  # Number of agent outputs logged
                "decision_steps_logged": 0,  # Number of decision steps logged
                "critique_records": 0,  # Number of critique records (bMAS)
                "clear_reasoning_path": False,  # Whether reasoning path is clear
                "trace_annotations": []  # Annotated trace events
            },
            
            # 4. Error Types and Failure Modes
            "error_types": {
                "wrong_math": 0,  # Wrong mathematical calculations
                "answer_extraction_issues": 0,  # Issues extracting answer
                "parsing_errors": 0,  # Parsing errors
                "llm_inconsistencies": 0,  # LLM inconsistencies
                "agent_failures": [],  # List of agent failure events
                "system_breakdowns": 0,  # Complete system breakdowns
                "failure_modes": [],  # Catalog of failure modes
                "error_distribution": {}  # Distribution of error types
            },
            
            # 5. Resource Utilization
            "resources": {
                "total_tokens": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "execution_time": 0.0,
                "cpu_usage": [],  # List of CPU usage samples
                "memory_usage": [],  # List of memory usage samples
                "peak_memory_mb": 0,
                "average_cpu_percent": 0.0,
                "rounds": 0,  # Number of rounds (for iterative systems)
                "agent_count": 0,  # Number of agents used
                "llm_calls": 0,  # Number of LLM API calls
                "resource_per_correct_answer": None,  # Calculated later
                "resource_per_incorrect_answer": None  # Calculated later
            },
            
            # 6. Quality Attribute Traceability
            "quality_attributes": {
                "modularity_evidence": [],  # Evidence of modular design
                "scalability_evidence": [],  # Evidence of scalability
                "transparency_evidence": [],  # Evidence of transparency
                "reliability_evidence": [],  # Evidence of reliability
                "error_recovery_events": [],  # Error recovery events
                "traceable_critiques": [],  # Traceable critique events
                "multi_system_comparison": {}  # For comparison across systems
            },
            
            # 7. User/Auditor Experience
            "user_experience": {
                "summary_log_quality": None,  # Quality score of summary log
                "side_by_side_tables": False,  # Whether side-by-side tables exist
                "correctness_reporting": None,  # Quality of correctness reporting
                "error_trace_quality": None,  # Quality of error trace
                "reasonableness_check": None,  # Whether answer is reasonable
                "insight_clarity": None,  # Clarity of insights provided
                "audit_trail_completeness": None  # Completeness of audit trail
            }
        }
    
    def start_tracking(self, problem: str, ground_truth: Optional[str] = None):
        """Start tracking metrics for a new experiment."""
        self.metrics["problem"] = problem
        self.metrics["ground_truth"] = ground_truth
        self.start_time = time.time()
        if self.process:
            try:
                self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            except Exception:
                self.start_memory = 0
        else:
            self.start_memory = 0
        
        # Reset resource tracking
        self.metrics["resources"]["cpu_usage"] = []
        self.metrics["resources"]["memory_usage"] = []
        self.metrics["resources"]["llm_calls"] = 0
    
    def track_agent_error(self, agent_name: str, error_type: str, error_message: str, 
                          recovered: bool = False, recovery_method: Optional[str] = None):
        """Track an agent error and potential recovery."""
        error_entry = {
            "agent": agent_name,
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat(),
            "recovered": recovered,
            "recovery_method": recovery_method
        }
        self.metrics["robustness"]["agent_errors"].append(error_entry)
        
        if recovered:
            self.metrics["robustness"]["resilience_episodes"] += 1
            if recovery_method == "critique":
                self.metrics["robustness"]["critique_recoveries"] += 1
            elif recovery_method == "voting":
                self.metrics["robustness"]["voting_recoveries"] += 1
            self.metrics["robustness"]["error_corrections"] += 1
    
    def track_outlier_detection(self, agent_name: str, outlier_type: str, description: str):
        """Track detection of an outlier agent output."""
        self.metrics["robustness"]["outlier_detections"] += 1
        self.metrics["robustness"]["agent_errors"].append({
            "agent": agent_name,
            "error_type": "outlier",
            "outlier_type": outlier_type,
            "description": description,
            "timestamp": datetime.now().isoformat()
        })
    
    def track_consensus_event(self, agents: List[str], consensus_method: str, 
                             round_num: int = 0, confidence: Optional[float] = None):
        """Track a consensus event."""
        consensus_entry = {
            "round": round_num,
            "agents": agents,
            "method": consensus_method,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }
        self.metrics["consensus"]["consensus_history"].append(consensus_entry)
        self.metrics["consensus"]["agents_in_consensus"] = agents
        self.metrics["consensus"]["consensus_set_size"] = len(agents)
        self.metrics["consensus"]["consensus_process"] = consensus_method
        self.metrics["consensus"]["rounds_to_consensus"] = round_num
        if confidence is not None:
            self.metrics["consensus"]["decision_confidence"] = confidence
    
    def track_critique(self, critic_name: str, critique_type: str, led_to_correction: bool = False):
        """Track a critique event (for bMAS systems)."""
        self.metrics["consensus"]["critiques_to_consensus"] += 1
        self.metrics["explainability"]["critique_records"] += 1
        
        if led_to_correction:
            self.metrics["robustness"]["critique_recoveries"] += 1
            self.metrics["robustness"]["error_corrections"] += 1
    
    def track_reasoning_step(self, step_description: str, agent_name: Optional[str] = None,
                           step_type: str = "reasoning"):
        """Track a reasoning step."""
        step_entry = {
            "description": step_description,
            "agent": agent_name,
            "type": step_type,
            "timestamp": datetime.now().isoformat()
        }
        self.metrics["explainability"]["reasoning_steps"].append(step_entry)
        self.metrics["explainability"]["reasoning_depth"] = len(self.metrics["explainability"]["reasoning_steps"])
    
    def track_decision_step(self, decision_description: str, agent_name: str):
        """Track a decision step."""
        self.track_reasoning_step(decision_description, agent_name, "decision")
        self.metrics["explainability"]["decision_steps_logged"] += 1
    
    def track_error_type(self, error_type: str, description: str, agent_name: Optional[str] = None):
        """Track a specific error type."""
        if error_type == "wrong_math":
            self.metrics["error_types"]["wrong_math"] += 1
        elif error_type == "answer_extraction":
            self.metrics["error_types"]["answer_extraction_issues"] += 1
        elif error_type == "parsing":
            self.metrics["error_types"]["parsing_errors"] += 1
        elif error_type == "llm_inconsistency":
            self.metrics["error_types"]["llm_inconsistencies"] += 1
        
        error_entry = {
            "type": error_type,
            "description": description,
            "agent": agent_name,
            "timestamp": datetime.now().isoformat()
        }
        self.metrics["error_types"]["failure_modes"].append(error_entry)
        
        # Update error distribution
        if error_type not in self.metrics["error_types"]["error_distribution"]:
            self.metrics["error_types"]["error_distribution"][error_type] = 0
        self.metrics["error_types"]["error_distribution"][error_type] += 1
    
    def track_agent_failure(self, agent_name: str, failure_type: str, outcome: str):
        """Track an agent failure."""
        failure_entry = {
            "agent": agent_name,
            "failure_type": failure_type,
            "outcome": outcome,
            "timestamp": datetime.now().isoformat()
        }
        self.metrics["error_types"]["agent_failures"].append(failure_entry)
        
        if outcome == "system_breakdown":
            self.metrics["error_types"]["system_breakdowns"] += 1
    
    def track_tokens(self, prompt_tokens: int = 0, completion_tokens: int = 0):
        """Track token usage."""
        self.metrics["resources"]["prompt_tokens"] += prompt_tokens
        self.metrics["resources"]["completion_tokens"] += completion_tokens
        self.metrics["resources"]["total_tokens"] += (prompt_tokens + completion_tokens)
        self.metrics["resources"]["llm_calls"] += 1
    
    def track_resource_sample(self):
        """Sample current resource usage."""
        if not self.process:
            return
        try:
            cpu_percent = self.process.cpu_percent(interval=0.1)
            memory_mb = self.process.memory_info().rss / 1024 / 1024
            
            self.metrics["resources"]["cpu_usage"].append(cpu_percent)
            self.metrics["resources"]["memory_usage"].append(memory_mb)
            
            if memory_mb > self.metrics["resources"]["peak_memory_mb"]:
                self.metrics["resources"]["peak_memory_mb"] = memory_mb
        except Exception:
            pass  # Ignore errors in resource tracking
    
    def track_round(self, round_num: int):
        """Track a round (for iterative systems)."""
        self.metrics["resources"]["rounds"] = round_num
        self.track_resource_sample()
    
    def track_agent_count(self, count: int):
        """Track the number of agents."""
        self.metrics["resources"]["agent_count"] = count
    
    def track_quality_attribute(self, attribute: str, evidence: str, event_type: str = "general"):
        """Track evidence of quality attributes."""
        if attribute == "modularity":
            self.metrics["quality_attributes"]["modularity_evidence"].append({
                "evidence": evidence,
                "type": event_type,
                "timestamp": datetime.now().isoformat()
            })
        elif attribute == "scalability":
            self.metrics["quality_attributes"]["scalability_evidence"].append({
                "evidence": evidence,
                "type": event_type,
                "timestamp": datetime.now().isoformat()
            })
        elif attribute == "transparency":
            self.metrics["quality_attributes"]["transparency_evidence"].append({
                "evidence": evidence,
                "type": event_type,
                "timestamp": datetime.now().isoformat()
            })
        elif attribute == "reliability":
            self.metrics["quality_attributes"]["reliability_evidence"].append({
                "evidence": evidence,
                "type": event_type,
                "timestamp": datetime.now().isoformat()
            })
    
    def track_error_recovery(self, recovery_event: Dict[str, Any]):
        """Track an error recovery event."""
        self.metrics["quality_attributes"]["error_recovery_events"].append(recovery_event)
    
    def track_traceable_critique(self, critique_event: Dict[str, Any]):
        """Track a traceable critique event."""
        self.metrics["quality_attributes"]["traceable_critiques"].append(critique_event)
    
    def track_agent_output(self, agent_name: str, output: str):
        """Track an agent output for explainability."""
        self.metrics["explainability"]["agent_outputs_logged"] += 1
        self.track_reasoning_step(f"Agent {agent_name} output: {output[:100]}...", agent_name, "output")
    
    def finalize(self, final_answer: str, correct: Optional[bool] = None):
        """Finalize metrics tracking and calculate derived metrics."""
        # Calculate execution time
        if self.start_time:
            self.metrics["resources"]["execution_time"] = time.time() - self.start_time
        
        # Calculate average CPU usage
        if self.metrics["resources"]["cpu_usage"]:
            self.metrics["resources"]["average_cpu_percent"] = sum(
                self.metrics["resources"]["cpu_usage"]
            ) / len(self.metrics["resources"]["cpu_usage"])
        
        # Calculate error recovery rate
        total_errors = len(self.metrics["robustness"]["agent_errors"])
        if total_errors > 0:
            self.metrics["robustness"]["error_recovery_rate"] = (
                self.metrics["robustness"]["resilience_episodes"] / total_errors
            )
        
        # Calculate final answer agreement rate (for multi-agent systems)
        if self.metrics["consensus"]["agents_in_consensus"]:
            # This would need to be calculated based on actual agent outputs
            # For now, we'll set it based on consensus set size
            consensus_size = self.metrics["consensus"]["consensus_set_size"]
            total_agents = self.metrics["resources"]["agent_count"]
            if total_agents > 0:
                self.metrics["consensus"]["final_answer_agreement_rate"] = consensus_size / total_agents
        
        # Calculate trace completeness
        trace_length = sum(
            len(step.get("description", "")) 
            for step in self.metrics["explainability"]["reasoning_steps"]
        )
        self.metrics["explainability"]["trace_length"] = trace_length
        
        # Determine if reasoning path is clear
        self.metrics["explainability"]["clear_reasoning_path"] = (
            len(self.metrics["explainability"]["reasoning_steps"]) > 0 and
            self.metrics["explainability"]["decision_steps_logged"] > 0
        )
        
        # Store final answer and correctness
        self.metrics["final_answer"] = final_answer
        self.metrics["correct"] = correct
        
        # Calculate resource per answer (if correctness is known)
        if correct is not None:
            if correct:
                self.metrics["resources"]["resource_per_correct_answer"] = {
                    "tokens": self.metrics["resources"]["total_tokens"],
                    "time": self.metrics["resources"]["execution_time"],
                    "rounds": self.metrics["resources"]["rounds"]
                }
            else:
                self.metrics["resources"]["resource_per_incorrect_answer"] = {
                    "tokens": self.metrics["resources"]["total_tokens"],
                    "time": self.metrics["resources"]["execution_time"],
                    "rounds": self.metrics["resources"]["rounds"]
                }
        
        # Final resource sample
        self.track_resource_sample()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics dictionary."""
        return self.metrics
    
    def save(self, filename: Optional[str] = None) -> str:
        """Save metrics to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.system_name}_metrics_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8', errors='replace') as f:
            json.dump(self.metrics, f, indent=2)
        
        return filepath
    
    def save_summary_report(self, filename: Optional[str] = None) -> str:
        """Save human-readable summary report."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.system_name}_metrics_summary_{timestamp}.txt"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8', errors='replace') as f:
            f.write("=" * 80 + "\n")
            f.write(f"COMPREHENSIVE METRICS REPORT - {self.system_name}\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Timestamp: {self.metrics['timestamp']}\n")
            f.write(f"Problem: {self.metrics.get('problem', 'N/A')[:200]}...\n")
            if self.metrics.get('ground_truth'):
                f.write(f"Ground Truth: {self.metrics['ground_truth']}\n")
            f.write(f"Final Answer: {self.metrics.get('final_answer', 'N/A')}\n")
            f.write(f"Correct: {self.metrics.get('correct', 'N/A')}\n\n")
            
            # 1. Robustness
            f.write("=" * 80 + "\n")
            f.write("1. ROBUSTNESS TO AGENT ERRORS AND OUTLIERS\n")
            f.write("=" * 80 + "\n")
            f.write(f"Total Agent Errors: {len(self.metrics['robustness']['agent_errors'])}\n")
            f.write(f"Error Corrections: {self.metrics['robustness']['error_corrections']}\n")
            f.write(f"Resilience Episodes: {self.metrics['robustness']['resilience_episodes']}\n")
            f.write(f"Outlier Detections: {self.metrics['robustness']['outlier_detections']}\n")
            f.write(f"Critique Recoveries: {self.metrics['robustness']['critique_recoveries']}\n")
            f.write(f"Voting Recoveries: {self.metrics['robustness']['voting_recoveries']}\n")
            if self.metrics['robustness']['error_recovery_rate'] is not None:
                f.write(f"Error Recovery Rate: {self.metrics['robustness']['error_recovery_rate']:.2%}\n")
            f.write("\n")
            
            # 2. Consensus
            f.write("=" * 80 + "\n")
            f.write("2. CONSENSUS AND DECISION QUALITY\n")
            f.write("=" * 80 + "\n")
            f.write(f"Consensus Set Size: {self.metrics['consensus']['consensus_set_size']}\n")
            f.write(f"Consensus Process: {self.metrics['consensus']['consensus_process']}\n")
            f.write(f"Rounds to Consensus: {self.metrics['consensus']['rounds_to_consensus']}\n")
            f.write(f"Critiques to Consensus: {self.metrics['consensus']['critiques_to_consensus']}\n")
            if self.metrics['consensus']['final_answer_agreement_rate'] is not None:
                f.write(f"Final Answer Agreement Rate: {self.metrics['consensus']['final_answer_agreement_rate']:.2%}\n")
            if self.metrics['consensus']['decision_confidence'] is not None:
                f.write(f"Decision Confidence: {self.metrics['consensus']['decision_confidence']:.2f}\n")
            f.write("\n")
            
            # 3. Explainability
            f.write("=" * 80 + "\n")
            f.write("3. EXPLAINABILITY AND TRANSPARENCY\n")
            f.write("=" * 80 + "\n")
            f.write(f"Reasoning Steps: {self.metrics['explainability']['reasoning_depth']}\n")
            f.write(f"Trace Length: {self.metrics['explainability']['trace_length']} characters\n")
            f.write(f"Agent Outputs Logged: {self.metrics['explainability']['agent_outputs_logged']}\n")
            f.write(f"Decision Steps Logged: {self.metrics['explainability']['decision_steps_logged']}\n")
            f.write(f"Critique Records: {self.metrics['explainability']['critique_records']}\n")
            f.write(f"Clear Reasoning Path: {self.metrics['explainability']['clear_reasoning_path']}\n")
            f.write("\n")
            
            # 4. Error Types
            f.write("=" * 80 + "\n")
            f.write("4. ERROR TYPES AND FAILURE MODES\n")
            f.write("=" * 80 + "\n")
            f.write(f"Wrong Math: {self.metrics['error_types']['wrong_math']}\n")
            f.write(f"Answer Extraction Issues: {self.metrics['error_types']['answer_extraction_issues']}\n")
            f.write(f"Parsing Errors: {self.metrics['error_types']['parsing_errors']}\n")
            f.write(f"LLM Inconsistencies: {self.metrics['error_types']['llm_inconsistencies']}\n")
            f.write(f"System Breakdowns: {self.metrics['error_types']['system_breakdowns']}\n")
            f.write(f"Total Agent Failures: {len(self.metrics['error_types']['agent_failures'])}\n")
            f.write("\n")
            
            # 5. Resource Utilization
            f.write("=" * 80 + "\n")
            f.write("5. RESOURCE UTILIZATION\n")
            f.write("=" * 80 + "\n")
            f.write(f"Total Tokens: {self.metrics['resources']['total_tokens']}\n")
            f.write(f"Prompt Tokens: {self.metrics['resources']['prompt_tokens']}\n")
            f.write(f"Completion Tokens: {self.metrics['resources']['completion_tokens']}\n")
            f.write(f"Execution Time: {self.metrics['resources']['execution_time']:.2f} seconds\n")
            f.write(f"Peak Memory: {self.metrics['resources']['peak_memory_mb']:.2f} MB\n")
            f.write(f"Average CPU: {self.metrics['resources']['average_cpu_percent']:.2f}%\n")
            f.write(f"Rounds: {self.metrics['resources']['rounds']}\n")
            f.write(f"Agent Count: {self.metrics['resources']['agent_count']}\n")
            f.write(f"LLM Calls: {self.metrics['resources']['llm_calls']}\n")
            f.write("\n")
            
            # 6. Quality Attributes
            f.write("=" * 80 + "\n")
            f.write("6. QUALITY ATTRIBUTE TRACEABILITY\n")
            f.write("=" * 80 + "\n")
            f.write(f"Modularity Evidence: {len(self.metrics['quality_attributes']['modularity_evidence'])} events\n")
            f.write(f"Scalability Evidence: {len(self.metrics['quality_attributes']['scalability_evidence'])} events\n")
            f.write(f"Transparency Evidence: {len(self.metrics['quality_attributes']['transparency_evidence'])} events\n")
            f.write(f"Reliability Evidence: {len(self.metrics['quality_attributes']['reliability_evidence'])} events\n")
            f.write(f"Error Recovery Events: {len(self.metrics['quality_attributes']['error_recovery_events'])}\n")
            f.write(f"Traceable Critiques: {len(self.metrics['quality_attributes']['traceable_critiques'])}\n")
            f.write("\n")
            
            # 7. User Experience
            f.write("=" * 80 + "\n")
            f.write("7. USER/AUDITOR EXPERIENCE\n")
            f.write("=" * 80 + "\n")
            f.write(f"Summary Log Quality: {self.metrics['user_experience']['summary_log_quality']}\n")
            f.write(f"Side-by-Side Tables: {self.metrics['user_experience']['side_by_side_tables']}\n")
            f.write(f"Correctness Reporting: {self.metrics['user_experience']['correctness_reporting']}\n")
            f.write(f"Error Trace Quality: {self.metrics['user_experience']['error_trace_quality']}\n")
            f.write(f"Clear Reasoning Path: {self.metrics['explainability']['clear_reasoning_path']}\n")
            f.write("\n")
            
            f.write("=" * 80 + "\n")
        
        return filepath

