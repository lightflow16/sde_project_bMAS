"""
Predefined agent implementations: Planner, Decider, Critic, Cleaner, ConflictResolver.
Using original implementation prompts and format.
"""
from typing import Dict, Any, Optional
import os
import sys

# Add parent directories to path for imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
_orig_dir = os.path.dirname(_current_dir)
_root_dir = os.path.dirname(_orig_dir)
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)
if _orig_dir not in sys.path:
    sys.path.insert(0, _orig_dir)

from .base_agent import Agent
from llm_integration.api import call_llm, parse_json_response
from prompts.predefined_prompts import (
    PLANNER_PROMPT,
    DECIDER_PROMPT,
    CRITIC_PROMPT,
    CLEANER_PROMPT,
    CONFLICT_RESOLVER_PROMPT
)


class PlannerAgent(Agent):
    """Agent responsible for creating plans and decomposing problems."""
    
    def __init__(self, name: str, llm_backend: str, blackboard):
        super().__init__(name, "planner", llm_backend, blackboard)
        self.system_prompt = "You are a strategic planner who breaks down complex problems into manageable steps."
    
    def act(self, problem: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a plan for solving the problem."""
        blackboard_state = self.read_blackboard()
        prompt = PLANNER_PROMPT.format(
            problem=problem,
            blackboard_state=blackboard_state
        )
        
        response = call_llm(prompt, self.llm_backend, system_prompt=self.system_prompt)
        parsed = parse_json_response(response["content"])
        
        # Original format: {"plan": "...", "steps": [...], "explanation": "..."}
        plan_content = parsed.get("plan", response["content"])
        steps = parsed.get("steps", [])
        explanation = parsed.get("explanation", "")
        
        if steps:
            plan_content = f"{plan_content}\nSteps: {', '.join(steps)}"
        if explanation:
            plan_content = f"{plan_content}\nExplanation: {explanation}"
        
        self.write_to_blackboard(plan_content, "plan", {"parsed_response": parsed})
        
        return {
            "agent": self.name,
            "response": parsed,
            "raw_response": response["content"],
            "tokens": response["metadata"].get("tokens_used", 0)
        }


class DeciderAgent(Agent):
    """Agent responsible for deciding when a solution is ready."""
    
    def __init__(self, name: str, llm_backend: str, blackboard):
        super().__init__(name, "decider", llm_backend, blackboard)
        self.system_prompt = "You are a decision-maker who evaluates when solutions are complete and ready."
    
    def act(self, problem: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Decide if solution is ready and provide final answer."""
        blackboard_state = self.read_blackboard()
        prompt = DECIDER_PROMPT.format(
            problem=problem,
            blackboard_state=blackboard_state
        )
        
        response = call_llm(prompt, self.llm_backend, system_prompt=self.system_prompt)
        parsed = parse_json_response(response["content"])
        
        # Original format: {"is_solution_ready": true/false, "final_answer": "...", "confidence": 0.0-1.0, "explanation": "..."}
        is_solution_ready = parsed.get("is_solution_ready", False)
        final_answer = parsed.get("final_answer", None)
        confidence = parsed.get("confidence", 0.0)
        explanation = parsed.get("explanation", "")
        
        # Write to blackboard
        decision_content = f"Solution ready: {is_solution_ready}\nFinal answer: {final_answer if final_answer else 'N/A'}\nConfidence: {confidence}"
        if explanation:
            decision_content += f"\nExplanation: {explanation}"
        self.write_to_blackboard(decision_content, "decision", {"parsed_response": parsed})
        
        return {
            "agent": self.name,
            "response": parsed,
            "raw_response": response["content"],
            "tokens": response["metadata"].get("tokens_used", 0),
            "is_solution_ready": is_solution_ready,
            "final_answer": final_answer
        }


class CriticAgent(Agent):
    """Agent responsible for critiquing and evaluating work."""
    
    def __init__(self, name: str, llm_backend: str, blackboard):
        super().__init__(name, "critic", llm_backend, blackboard)
        self.system_prompt = "You are a critical evaluator who identifies issues and suggests improvements."
    
    def act(self, problem: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Provide critique of current blackboard state."""
        blackboard_state = self.read_blackboard()
        prompt = CRITIC_PROMPT.format(
            problem=problem,
            blackboard_state=blackboard_state
        )
        
        response = call_llm(prompt, self.llm_backend, system_prompt=self.system_prompt)
        parsed = parse_json_response(response["content"])
        
        # Original format: {"critic_list": [{"issue": "...", "severity": "high/medium/low", "suggestion": "..."}], "explanation": "..."}
        critic_list = parsed.get("critic_list", [])
        explanation = parsed.get("explanation", "")
        
        critique_content = f"Critic list: {critic_list}"
        if explanation:
            critique_content += f"\nExplanation: {explanation}"
        
        self.write_to_blackboard(critique_content, "critique", {"parsed_response": parsed})
        
        return {
            "agent": self.name,
            "response": parsed,
            "raw_response": response["content"],
            "tokens": response["metadata"].get("tokens_used", 0)
        }


class CleanerAgent(Agent):
    """Agent responsible for cleaning and organizing blackboard content."""
    
    def __init__(self, name: str, llm_backend: str, blackboard):
        super().__init__(name, "cleaner", llm_backend, blackboard)
        self.system_prompt = "You are an organizer who cleans up and structures information effectively."
    
    def act(self, problem: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Clean and organize blackboard content."""
        blackboard_state = self.read_blackboard()
        prompt = CLEANER_PROMPT.format(
            problem=problem,
            blackboard_state=blackboard_state
        )
        
        response = call_llm(prompt, self.llm_backend, system_prompt=self.system_prompt)
        parsed = parse_json_response(response["content"])
        
        # Original format: {"cleaned_content": "...", "removed_items": [...], "summary": "..."}
        cleaned_content = parsed.get("cleaned_content", "")
        removed_items = parsed.get("removed_items", [])
        summary = parsed.get("summary", "")
        
        if removed_items:
            cleaned_content += f"\nRemoved items: {', '.join(removed_items)}"
        if summary:
            cleaned_content += f"\nSummary: {summary}"
        
        self.write_to_blackboard(cleaned_content, "cleaned", {"parsed_response": parsed})
        
        return {
            "agent": self.name,
            "response": parsed,
            "raw_response": response["content"],
            "tokens": response["metadata"].get("tokens_used", 0)
        }


class ConflictResolverAgent(Agent):
    """Agent responsible for resolving conflicts between agents."""
    
    def __init__(self, name: str, llm_backend: str, blackboard):
        super().__init__(name, "conflict_resolver", llm_backend, blackboard)
        self.system_prompt = "You are a mediator who resolves conflicts and finds common ground."
    
    def act(self, problem: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Resolve conflicts in blackboard."""
        blackboard_state = self.read_blackboard()
        prompt = CONFLICT_RESOLVER_PROMPT.format(
            problem=problem,
            blackboard_state=blackboard_state
        )
        
        response = call_llm(prompt, self.llm_backend, system_prompt=self.system_prompt)
        parsed = parse_json_response(response["content"])
        
        # Original format: {"conflicts": [{"description": "...", "agents_involved": [...], "resolution": "..."}], "explanation": "..."}
        conflicts = parsed.get("conflicts", [])
        explanation = parsed.get("explanation", "")
        
        resolution_content = f"Conflicts: {conflicts}"
        if explanation:
            resolution_content += f"\nExplanation: {explanation}"
        
        self.write_to_blackboard(resolution_content, "resolution", {"parsed_response": parsed})
        
        return {
            "agent": self.name,
            "response": parsed,
            "raw_response": response["content"],
            "tokens": response["metadata"].get("tokens_used", 0)
        }

