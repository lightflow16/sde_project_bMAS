"""
Static agent implementations for Static MAS.
All agents solve problems independently without blackboard.
"""
from typing import Dict, Any
from .base_agent import StaticAgent
import sys
import os

# Add parent directory to path to import shared modules
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from llm_integration.api import call_llm, parse_json_response, random_model_choice
from static_mas.prompts import STATIC_PROMPTS


class MathematicsExpertAgent(StaticAgent):
    """Mathematics expert agent."""
    
    def __init__(self, name: str, llm_backend: str = None):
        if llm_backend is None:
            llm_backend = random_model_choice()
        super().__init__(name, "mathematics_expert", llm_backend)
        self.system_prompt = "You are an expert mathematician specializing in problem-solving, proofs, and mathematical reasoning."
    
    def solve(self, problem: str) -> Dict[str, Any]:
        """Solve the problem using mathematical expertise."""
        prompt = STATIC_PROMPTS["mathematics_expert"].format(problem=problem)
        response = call_llm(prompt, self.llm_backend, system_prompt=self.system_prompt)
        parsed = parse_json_response(response["content"])
        
        return {
            "agent": self.name,
            "role": self.role,
            "answer": parsed.get("answer", response["content"]),
            "confidence": parsed.get("confidence", 0.5),
            "explanation": parsed.get("explanation", ""),
            "raw_response": response["content"],
            "tokens": response["metadata"].get("tokens_used", 0),
            "parsed_response": parsed
        }


class PhysicsExpertAgent(StaticAgent):
    """Physics expert agent."""
    
    def __init__(self, name: str, llm_backend: str = None):
        if llm_backend is None:
            llm_backend = random_model_choice()
        super().__init__(name, "physics_expert", llm_backend)
        self.system_prompt = "You are an expert physicist specializing in physical principles, mechanics, and scientific reasoning."
    
    def solve(self, problem: str) -> Dict[str, Any]:
        """Solve the problem using physics expertise."""
        prompt = STATIC_PROMPTS["physics_expert"].format(problem=problem)
        response = call_llm(prompt, self.llm_backend, system_prompt=self.system_prompt)
        parsed = parse_json_response(response["content"])
        
        return {
            "agent": self.name,
            "role": self.role,
            "answer": parsed.get("answer", response["content"]),
            "confidence": parsed.get("confidence", 0.5),
            "explanation": parsed.get("explanation", ""),
            "raw_response": response["content"],
            "tokens": response["metadata"].get("tokens_used", 0),
            "parsed_response": parsed
        }


class LogicReasoningExpertAgent(StaticAgent):
    """Logic and reasoning expert agent."""
    
    def __init__(self, name: str, llm_backend: str = None):
        if llm_backend is None:
            llm_backend = random_model_choice()
        super().__init__(name, "logic_reasoning_expert", llm_backend)
        self.system_prompt = "You are an expert in logical reasoning, deductive and inductive reasoning, and problem-solving strategies."
    
    def solve(self, problem: str) -> Dict[str, Any]:
        """Solve the problem using logical reasoning."""
        prompt = STATIC_PROMPTS["logic_reasoning_expert"].format(problem=problem)
        response = call_llm(prompt, self.llm_backend, system_prompt=self.system_prompt)
        parsed = parse_json_response(response["content"])
        
        return {
            "agent": self.name,
            "role": self.role,
            "answer": parsed.get("answer", response["content"]),
            "confidence": parsed.get("confidence", 0.5),
            "explanation": parsed.get("explanation", ""),
            "raw_response": response["content"],
            "tokens": response["metadata"].get("tokens_used", 0),
            "parsed_response": parsed
        }


class PlannerAgent(StaticAgent):
    """Planner agent - creates plans and solves problems."""
    
    def __init__(self, name: str, llm_backend: str = None):
        if llm_backend is None:
            llm_backend = random_model_choice()
        super().__init__(name, "planner", llm_backend)
        self.system_prompt = "You are a strategic planner who breaks down complex problems into manageable steps and solves them."
    
    def solve(self, problem: str) -> Dict[str, Any]:
        """Solve the problem by creating a plan and executing it."""
        prompt = STATIC_PROMPTS["planner"].format(problem=problem)
        response = call_llm(prompt, self.llm_backend, system_prompt=self.system_prompt)
        parsed = parse_json_response(response["content"])
        
        # Ensure answer is a string
        answer = parsed.get("answer") or parsed.get("final_answer") or response["content"]
        if not isinstance(answer, str):
            answer = str(answer)
        
        return {
            "agent": self.name,
            "role": self.role,
            "answer": answer,
            "confidence": parsed.get("confidence", 0.5) if isinstance(parsed, dict) else 0.5,
            "explanation": parsed.get("explanation", "") if isinstance(parsed, dict) else "",
            "raw_response": response["content"],
            "tokens": response["metadata"].get("tokens_used", 0),
            "parsed_response": parsed
        }


class DeciderAgent(StaticAgent):
    """Decider agent - makes final decisions."""
    
    def __init__(self, name: str, llm_backend: str = None):
        if llm_backend is None:
            llm_backend = random_model_choice()
        super().__init__(name, "decider", llm_backend)
        self.system_prompt = "You are a decision-maker who evaluates problems and provides final answers."
    
    def solve(self, problem: str) -> Dict[str, Any]:
        """Solve the problem and provide a final answer."""
        prompt = STATIC_PROMPTS["decider"].format(problem=problem)
        response = call_llm(prompt, self.llm_backend, system_prompt=self.system_prompt)
        parsed = parse_json_response(response["content"])
        
        return {
            "agent": self.name,
            "role": self.role,
            "answer": parsed.get("answer", parsed.get("final_answer", response["content"])),
            "confidence": parsed.get("confidence", 0.5),
            "explanation": parsed.get("explanation", ""),
            "raw_response": response["content"],
            "tokens": response["metadata"].get("tokens_used", 0),
            "parsed_response": parsed
        }


class GeneralExpertAgent(StaticAgent):
    """General expert agent for diverse problems."""
    
    def __init__(self, name: str, llm_backend: str = None):
        if llm_backend is None:
            llm_backend = random_model_choice()
        super().__init__(name, "general_expert", llm_backend)
        self.system_prompt = "You are a general problem-solving expert with broad knowledge across multiple domains."
    
    def solve(self, problem: str) -> Dict[str, Any]:
        """Solve the problem using general expertise."""
        prompt = STATIC_PROMPTS["general_expert"].format(problem=problem)
        response = call_llm(prompt, self.llm_backend, system_prompt=self.system_prompt)
        parsed = parse_json_response(response["content"])
        
        return {
            "agent": self.name,
            "role": self.role,
            "answer": parsed.get("answer", response["content"]),
            "confidence": parsed.get("confidence", 0.5),
            "explanation": parsed.get("explanation", ""),
            "raw_response": response["content"],
            "tokens": response["metadata"].get("tokens_used", 0),
            "parsed_response": parsed
        }


def create_static_agent_pool() -> list:
    """
    Create a pool of static agents with fixed roles.
    No dynamic generation - all agents are predefined.
    
    Returns:
        List of agent objects
    """
    agents = []
    
    # Create fixed set of agents
    agent_configs = [
        ("mathematics_expert_1", MathematicsExpertAgent),
        ("mathematics_expert_2", MathematicsExpertAgent),
        ("physics_expert", PhysicsExpertAgent),
        ("logic_reasoning_expert", LogicReasoningExpertAgent),
        ("planner", PlannerAgent),
        ("decider", DeciderAgent),
        ("general_expert", GeneralExpertAgent),
    ]
    
    for name, agent_class in agent_configs:
        agent = agent_class(name)
        agents.append(agent)
    
    return agents

