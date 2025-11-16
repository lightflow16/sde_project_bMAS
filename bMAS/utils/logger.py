"""
Enhanced logging and tracing system for LbMAS experiments.
Captures prompts, responses, agent selections, and full execution traces.
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class ExperimentLogger:
    """
    Logger for capturing detailed experiment traces.
    """
    
    def __init__(self, experiment_id: Optional[str] = None, output_dir: str = "outputs"):
        """
        Initialize logger.
        
        Args:
            experiment_id: Unique identifier for this experiment
            output_dir: Directory to save logs
        """
        self.experiment_id = experiment_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.trace = {
            "experiment_id": self.experiment_id,
            "start_time": datetime.now().isoformat(),
            "problem": None,
            "ground_truth": None,
            "agent_pool": [],
            "rounds": [],
            "prompts": [],
            "final_answer": None,
            "end_time": None,
            "total_tokens": 0
        }
    
    def log_problem(self, problem: str, ground_truth: Optional[str] = None):
        """Log the problem/question."""
        self.trace["problem"] = problem
        self.trace["ground_truth"] = ground_truth
    
    def log_agent_pool(self, agents: List[Any]):
        """Log all agents in the pool."""
        self.trace["agent_pool"] = [
            {
                "name": agent.name,
                "role": agent.role,
                "type": "predefined" if hasattr(agent, '__class__') and "predefined" in str(agent.__class__.__module__) else "generated",
                "llm_backend": agent.llm_backend,
                "description": getattr(agent, 'description', None)
            }
            for agent in agents
        ]
    
    def log_prompt(self, agent_name: str, prompt_type: str, prompt: str, 
                   system_prompt: Optional[str] = None):
        """Log a prompt sent to an agent."""
        prompt_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "type": prompt_type,  # "agent_action", "control_unit", "agent_generation"
            "prompt": prompt,
            "system_prompt": system_prompt
        }
        self.trace["prompts"].append(prompt_entry)
        return len(self.trace["prompts"]) - 1  # Return index for linking
    
    def log_agent_response(self, agent_name: str, response: Dict[str, Any], 
                           prompt_index: Optional[int] = None):
        """Log an agent's response."""
        response_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "response_content": response.get("content", ""),
            "parsed_response": response.get("response", {}),
            "tokens": response.get("tokens", 0),
            "prompt_index": prompt_index
        }
        return response_entry
    
    def log_round_start(self, round_num: int, blackboard_state: str):
        """Log the start of a round."""
        round_entry = {
            "round": round_num,
            "start_time": datetime.now().isoformat(),
            "blackboard_state": blackboard_state,
            "selected_agents": [],
            "agent_actions": [],
            "end_time": None
        }
        self.trace["rounds"].append(round_entry)
        return len(self.trace["rounds"]) - 1
    
    def log_agent_selection(self, round_index: int, selected_agents: List[str], 
                           reasoning: str, control_unit_response: str):
        """Log agent selection by control unit."""
        if round_index < len(self.trace["rounds"]):
            self.trace["rounds"][round_index]["selected_agents"] = selected_agents
            self.trace["rounds"][round_index]["selection_reasoning"] = reasoning
            self.trace["rounds"][round_index]["control_unit_response"] = control_unit_response
    
    def log_agent_action(self, round_index: int, agent_name: str, 
                        action_result: Dict[str, Any], blackboard_update: str):
        """Log an agent's action in a round."""
        if round_index < len(self.trace["rounds"]):
            action_entry = {
                "agent": agent_name,
                "timestamp": datetime.now().isoformat(),
                "result": action_result,
                "blackboard_update": blackboard_update
            }
            self.trace["rounds"][round_index]["agent_actions"].append(action_entry)
    
    def log_round_end(self, round_index: int):
        """Log the end of a round."""
        if round_index < len(self.trace["rounds"]):
            self.trace["rounds"][round_index]["end_time"] = datetime.now().isoformat()
    
    def log_final_answer(self, answer: str, source: str, is_solution_ready: bool):
        """Log the final answer."""
        self.trace["final_answer"] = answer
        self.trace["answer_source"] = source
        self.trace["is_solution_ready"] = is_solution_ready
    
    def log_blackboard_snapshot(self, round_index: int, blackboard: Any):
        """Log a snapshot of the blackboard state."""
        if round_index < len(self.trace["rounds"]):
            snapshot = {
                "public_messages": blackboard.public_space.copy(),
                "private_spaces": {
                    key: messages.copy() 
                    for key, messages in blackboard.private_spaces.items()
                },
                "round": blackboard.metadata["round"]
            }
            self.trace["rounds"][round_index]["blackboard_snapshot"] = snapshot
    
    def add_tokens(self, tokens: int):
        """Add to total token count."""
        self.trace["total_tokens"] += tokens
    
    def save(self, filename: Optional[str] = None):
        """Save the trace to a JSON file."""
        self.trace["end_time"] = datetime.now().isoformat()
        
        if filename is None:
            filename = f"trace_{self.experiment_id}.json"
        
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8', errors='replace') as f:
            json.dump(self.trace, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def generate_text_report(self) -> str:
        """Generate a human-readable text report."""
        lines = []
        lines.append("="*80)
        lines.append("LbMAS EXPERIMENT TRACE")
        lines.append("="*80)
        lines.append(f"Experiment ID: {self.trace['experiment_id']}")
        lines.append(f"Start Time: {self.trace['start_time']}")
        lines.append(f"End Time: {self.trace.get('end_time', 'In Progress')}")
        lines.append("")
        
        lines.append("-"*80)
        lines.append("PROBLEM")
        lines.append("-"*80)
        lines.append(f"Question: {self.trace['problem']}")
        if self.trace.get('ground_truth'):
            lines.append(f"Ground Truth: {self.trace['ground_truth']}")
        lines.append("")
        
        lines.append("-"*80)
        lines.append("AGENT POOL")
        lines.append("-"*80)
        for agent in self.trace['agent_pool']:
            agent_type = agent.get('type', 'unknown').upper()
            lines.append(f"{agent['name']} ({agent['role']}) - {agent_type}")
            lines.append(f"  Backend: {agent['llm_backend']}")
            if agent.get('description'):
                lines.append(f"  Description: {agent['description']}")
        lines.append("")
        
        lines.append("-"*80)
        lines.append("EXECUTION TRACE")
        lines.append("-"*80)
        
        for round_entry in self.trace['rounds']:
            lines.append(f"\nROUND {round_entry['round']}")
            lines.append("-"*40)
            lines.append(f"Start: {round_entry['start_time']}")
            
            # Agent selection
            selected = round_entry.get('selected_agents', [])
            lines.append(f"\nSelected Agents: {', '.join(selected)}")
            if 'selection_reasoning' in round_entry:
                lines.append(f"Reasoning: {round_entry['selection_reasoning']}")
            
            # Agent actions
            lines.append("\nAgent Actions:")
            for action in round_entry.get('agent_actions', []):
                lines.append(f"  [{action['timestamp']}] {action['agent']}:")
                result = action.get('result', {})
                if 'response' in result:
                    response_preview = str(result['response'])[:200]
                    lines.append(f"    Response: {response_preview}...")
                if 'tokens' in result:
                    lines.append(f"    Tokens: {result['tokens']}")
                if 'blackboard_update' in action:
                    lines.append(f"    Blackboard Update: {action['blackboard_update'][:100]}...")
            
            # Blackboard state
            if 'blackboard_snapshot' in round_entry:
                snapshot = round_entry['blackboard_snapshot']
                public_count = len(snapshot.get('public_messages', []))
                private_count = len(snapshot.get('private_spaces', {}))
                lines.append(f"\nBlackboard State: {public_count} public messages, {private_count} private spaces")
            
            lines.append(f"End: {round_entry.get('end_time', 'In Progress')}")
            lines.append("")
        
        lines.append("-"*80)
        lines.append("FINAL ANSWER")
        lines.append("-"*80)
        lines.append(f"Answer: {self.trace.get('final_answer', 'N/A')}")
        lines.append(f"Source: {self.trace.get('answer_source', 'N/A')}")
        lines.append(f"Solution Ready: {self.trace.get('is_solution_ready', False)}")
        lines.append(f"Total Tokens: {self.trace.get('total_tokens', 0)}")
        lines.append("")
        
        lines.append("="*80)
        
        return "\n".join(lines)
    
    def save_text_report(self, filename: Optional[str] = None):
        """Save text report to file."""
        if filename is None:
            filename = f"report_{self.experiment_id}.txt"
        
        filepath = self.output_dir / filename
        report = self.generate_text_report()
        with open(filepath, 'w', encoding='utf-8', errors='replace') as f:
            f.write(report)
        
        return filepath

