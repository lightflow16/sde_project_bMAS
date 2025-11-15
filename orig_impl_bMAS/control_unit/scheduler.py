"""
Control unit for managing agent selection and execution rounds.
Using original implementation prompts and format.
"""
from typing import List, Dict, Any, Optional
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

from blackboard.blackboard import Blackboard
from agents.base_agent import Agent
from llm_integration.api import call_llm, parse_json_response, random_model_choice
from prompts.predefined_prompts import CONTROL_UNIT_PROMPT
import config


class ControlUnit:
    """
    Control unit that selects agents for each round based on blackboard state.
    """
    
    def __init__(self, agents: List[Agent], blackboard: Blackboard, llm_backend: Optional[str] = None):
        """
        Initialize the control unit.
        
        Args:
            agents: List of all available agents
            blackboard: Reference to the blackboard
            llm_backend: Optional LLM backend for control unit (None for random)
        """
        self.agents = agents
        self.blackboard = blackboard
        self.llm_backend = llm_backend or random_model_choice()
        self.round_history: List[Dict[str, Any]] = []
    
    def get_agent_descriptions(self) -> str:
        """Get formatted descriptions of all available agents."""
        descriptions = []
        for agent in self.agents:
            desc = f"- {agent.name} ({agent.role})"
            if hasattr(agent, 'description'):
                desc += f": {agent.description}"
            descriptions.append(desc)
        return "\n".join(descriptions)
    
    def choose_agents_for_round(self, problem: str, require_critic: bool = False) -> List[str]:
        """
        Select agents to act in the current round.
        
        Args:
            problem: The problem being solved
            require_critic: If True, ensure critic is included (for validation)
            
        Returns:
            List of agent names to execute
        """
        blackboard_state = self.blackboard.get_all_messages_summary()
        agent_descriptions = self.get_agent_descriptions()
        
        # If critic validation is required, modify prompt
        if require_critic:
            # Check if decider has marked solution ready
            decider_messages = self.blackboard.get_public_messages("decision")
            if decider_messages:
                last_decision = decider_messages[-1]
                if "solution ready: True" in last_decision.get("content", "").lower():
                    # Force include critic for validation
                    prompt = CONTROL_UNIT_PROMPT.format(
                        problem=problem,
                        blackboard_state=blackboard_state + "\n\nIMPORTANT: The decider has marked the solution as ready. You MUST include the critic agent to validate the solution before finalizing.",
                        agent_descriptions=agent_descriptions
                    )
                else:
                    prompt = CONTROL_UNIT_PROMPT.format(
                        problem=problem,
                        blackboard_state=blackboard_state,
                        agent_descriptions=agent_descriptions
                    )
            else:
                prompt = CONTROL_UNIT_PROMPT.format(
                    problem=problem,
                    blackboard_state=blackboard_state,
                    agent_descriptions=agent_descriptions
                )
        else:
            prompt = CONTROL_UNIT_PROMPT.format(
                problem=problem,
                blackboard_state=blackboard_state,
                agent_descriptions=agent_descriptions
            )
        
        response = call_llm(prompt, self.llm_backend)
        parsed = parse_json_response(response["content"])
        
        # Original format uses "selected_agents" (with underscore)
        selected_agent_names = parsed.get("selected_agents", [])
        
        # Validate that selected agents exist
        available_names = {agent.name for agent in self.agents}
        valid_selected = [name for name in selected_agent_names if name in available_names]
        
        # Ensure critic is included if validation is required
        if require_critic:
            critic_agents = [agent.name for agent in self.agents if "critic" in agent.role.lower()]
            if critic_agents and critic_agents[0] not in valid_selected:
                valid_selected.append(critic_agents[0])
        
        # If no valid agents selected, default to a subset
        if not valid_selected:
            # Default: select planner and decider if available
            default_names = ["planner", "decider", "critic"]
            valid_selected = [agent.name for agent in self.agents 
                            if any(default in agent.name.lower() or default in agent.role.lower() 
                                  for default in default_names)]
            if not valid_selected:
                # Last resort: select first few agents
                valid_selected = [agent.name for agent in self.agents[:3]]
        
        # Record selection
        self.round_history.append({
            "round": self.blackboard.metadata["round"],
            "selected_agents": valid_selected,
            "reasoning": parsed.get("reasoning", "Default selection"),
            "raw_response": response["content"]
        })
        
        return valid_selected
    
    def get_agents_by_names(self, agent_names: List[str]) -> List[Agent]:
        """Get agent objects by their names."""
        agent_dict = {agent.name: agent for agent in self.agents}
        return [agent_dict[name] for name in agent_names if name in agent_dict]

