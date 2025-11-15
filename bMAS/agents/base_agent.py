"""
Base agent class for all agents in the multi-agent system.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from blackboard.blackboard import Blackboard


class Agent(ABC):
    """
    Base class for all agents in the LbMAS system.
    """
    
    def __init__(self, name: str, role: str, llm_backend: str, blackboard: Blackboard):
        """
        Initialize an agent.
        
        Args:
            name: Unique name for the agent
            role: Role description (e.g., "planner", "critic")
            llm_backend: LLM backend identifier ("llama" or "qwen")
            blackboard: Reference to the shared blackboard
        """
        self.name = name
        self.role = role
        self.llm_backend = llm_backend
        self.blackboard = blackboard
        self.system_prompt = ""
    
    @abstractmethod
    def act(self, problem: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the agent's action based on current blackboard state.
        
        Args:
            problem: The problem/question to solve
            context: Optional additional context
            
        Returns:
            Dictionary with agent's response, including message content and metadata
        """
        pass
    
    def read_blackboard(self) -> str:
        """Get current blackboard state as formatted string."""
        return self.blackboard.get_all_messages_summary()
    
    def write_to_blackboard(self, content: str, message_type: str = "message",
                           metadata: Optional[Dict[str, Any]] = None) -> None:
        """Write a message to the public blackboard."""
        self.blackboard.add_public_message(self.name, content, message_type, metadata)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, role={self.role}, backend={self.llm_backend})"

