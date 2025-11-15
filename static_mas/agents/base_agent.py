"""
Base agent class for Static MAS - simplified without blackboard.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class StaticAgent(ABC):
    """
    Base class for all agents in the Static MAS system.
    No blackboard - agents work independently.
    """
    
    def __init__(self, name: str, role: str, llm_backend: str):
        """
        Initialize an agent.
        
        Args:
            name: Unique name for the agent
            role: Role description (e.g., "mathematics_expert", "planner")
            llm_backend: LLM backend identifier ("llama" or "qwen")
        """
        self.name = name
        self.role = role
        self.llm_backend = llm_backend
        self.system_prompt = ""
    
    @abstractmethod
    def solve(self, problem: str) -> Dict[str, Any]:
        """
        Solve the problem independently (no blackboard context).
        
        Args:
            problem: The problem/question to solve
            
        Returns:
            Dictionary with agent's response, answer, confidence, and metadata
        """
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, role={self.role}, backend={self.llm_backend})"

