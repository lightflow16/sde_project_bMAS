"""
Predefined agent implementations: Planner, Decider, Critic, Cleaner, ConflictResolver.
"""
from typing import Dict, Any, Optional
import os
import sys
import re

# Add parent directories to path for imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
_bmas_dir = os.path.dirname(_current_dir)
_root_dir = os.path.dirname(_bmas_dir)
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)
if _bmas_dir not in sys.path:
    sys.path.insert(0, _bmas_dir)

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
        
        # Paper format: {"[problem]": "...", "[planning]": "..."} or {"there is no need to decompose tasks, waiting for more information"}
        if "[problem]" in parsed and "[planning]" in parsed:
            plan_content = f"Problem: {parsed.get('[problem]', '')}\nPlanning: {parsed.get('[planning]', '')}"
        elif "there is no need to decompose tasks, waiting for more information" in str(parsed):
            plan_content = "No need to decompose tasks, waiting for more information"
        else:
            # Fallback to old format or raw content
            plan_content = parsed.get("plan", parsed.get("[planning]", response["content"]))
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
        
        # Paper format: {"the final answer is boxed[answer]"} or {"continue, waiting for more information"}
        final_answer = None
        is_solution_ready = False
        
        # Check for paper format
        if "the final answer is boxed" in str(parsed):
            # Extract answer from "the final answer is boxed[answer]"
            for key, value in parsed.items():
                if "the final answer is boxed" in str(value) or "boxed" in str(value):
                    # Try to extract the answer
                    match = re.search(r'boxed\[(.*?)\]', str(value))
                    if match:
                        final_answer = match.group(1)
                    else:
                        final_answer = str(value).replace("the final answer is boxed", "").strip("[]")
                    is_solution_ready = True
                    break
        elif "continue, waiting for more information" in str(parsed):
            is_solution_ready = False
        else:
            # Fallback to old format
            is_solution_ready = parsed.get("is_solution_ready", False)
            final_answer = parsed.get("final_answer", None)
        
        # Write to blackboard
        decision_content = f"Solution ready: {is_solution_ready}\nFinal answer: {final_answer if final_answer else 'N/A'}"
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
        
        # Paper format: {"critic list": [{"wrong message": "...", "explanation": "..."}]} or {"no problem, waiting for more information"}
        if "critic list" in parsed:
            critique_content = f"Critic list: {parsed.get('critic list', [])}"
        elif "no problem, waiting for more information" in str(parsed):
            critique_content = "No problem, waiting for more information"
        else:
            # Fallback to old format
            critique_content = parsed.get("explanation", response["content"])
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
        
        # Paper format: {"clean list": [{"useless message": "...", "explanation": "..."}]} or {"no useless messages, waiting for more information"}
        if "clean list" in parsed:
            cleaned_content = f"Clean list: {parsed.get('clean list', [])}"
        elif "no useless messages, waiting for more information" in str(parsed):
            cleaned_content = "No useless messages, waiting for more information"
        else:
            # Fallback to old format
            cleaned_content = parsed.get("cleaned_content", parsed.get("summary", response["content"]))
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
        
        # Paper format: {"conflict list": [{"agent": "...", "message": "..."}]} or {"no conflicts, waiting for more information"}
        if "conflict list" in parsed:
            resolution_content = f"Conflict list: {parsed.get('conflict list', [])}"
        elif "no conflicts, waiting for more information" in str(parsed):
            resolution_content = "No conflicts, waiting for more information"
        else:
            # Fallback to old format
            resolution_content = parsed.get("explanation", response["content"])
        self.write_to_blackboard(resolution_content, "resolution", {"parsed_response": parsed})
        
        return {
            "agent": self.name,
            "response": parsed,
            "raw_response": response["content"],
            "tokens": response["metadata"].get("tokens_used", 0)
        }

