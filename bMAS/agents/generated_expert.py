"""
Dynamically generated expert agents based on problem domain.
"""
from typing import Dict, Any, Optional, List
import os
import sys

# Add parent directories to path for imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
_bmas_dir = os.path.dirname(_current_dir)
_root_dir = os.path.dirname(_bmas_dir)
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)
if _bmas_dir not in sys.path:
    sys.path.insert(0, _bmas_dir)

from .base_agent import Agent
from llm_integration.api import call_llm, parse_json_response, random_model_choice
from prompts.predefined_prompts import EXPERT_AGENT_PROMPT_TEMPLATE


class GeneratedExpertAgent(Agent):
    """Expert agent generated dynamically based on problem domain."""
    
    def __init__(self, name: str, role: str, description: str, llm_backend: Optional[str] = None, blackboard=None):
        """
        Initialize a generated expert agent.
        
        Args:
            name: Unique name for the agent
            role: Expert role (e.g., "mathematics_expert")
            description: Description of expertise
            llm_backend: LLM backend (None for random selection)
            blackboard: Reference to blackboard
        """
        if llm_backend is None:
            llm_backend = random_model_choice()
        super().__init__(name, role, llm_backend, blackboard)
        self.description = description
        self.system_prompt = f"You are an expert {role} with the following expertise: {description}"
    
    def act(self, problem: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Provide expert analysis based on domain knowledge."""
        blackboard_state = self.read_blackboard()
        prompt = EXPERT_AGENT_PROMPT_TEMPLATE.format(
            role_name=self.name,
            role=self.role,
            roles_description=self.description,
            problem=problem,
            blackboard_state=blackboard_state
        )
        
        response = call_llm(prompt, self.llm_backend, system_prompt=self.system_prompt)
        parsed = parse_json_response(response["content"])
        
        # Paper format: {"output": ""}
        if "output" in parsed:
            expert_content = parsed.get("output", "")
        else:
            # Fallback to old format
            expert_content = parsed.get("expert_analysis", parsed.get("contribution", response["content"]))
        self.write_to_blackboard(expert_content, "expert_analysis", {
            "parsed_response": parsed,
            "role": self.role
        })
        
        return {
            "agent": self.name,
            "response": parsed,
            "raw_response": response["content"],
            "tokens": response["metadata"].get("tokens_used", 0)
        }


def generate_expert_agents(problem: str, llm_backend: Optional[str] = None) -> List[Dict[str, str]]:
    """
    Generate expert agent descriptions based on the problem.
    
    Args:
        problem: The problem/question to solve
        llm_backend: Optional LLM backend for generation
        
    Returns:
        List of dictionaries with 'role' and 'description' keys
    """
    from prompts.predefined_prompts import AGENT_GENERATION_PROMPT
    
    prompt = AGENT_GENERATION_PROMPT.format(problem=problem)
    response = call_llm(prompt, llm_backend)
    parsed = parse_json_response(response["content"])
    
    # Paper format: dictionary of roles {"role name": "description"}
    # Check if response is in dictionary format (paper format)
    experts = []
    if isinstance(parsed, dict):
        # Check if it's the old array format
        if "experts" in parsed:
            experts = parsed["experts"]
        else:
            # Paper format: dictionary where keys are role names and values are descriptions
            # Convert to list format: [{"role": "...", "description": "..."}]
            for role_name, description in parsed.items():
                if isinstance(description, str) and role_name not in ["raw_response", "content"]:
                    experts.append({"role": role_name, "description": description})
    
    if not experts:
        # Fallback: create a default expert if parsing fails
        experts = [{"role": "general_expert", "description": "A general problem-solving expert"}]
    
    return experts

