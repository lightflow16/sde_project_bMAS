"""
Blackboard module for shared memory in multi-agent system.
Implements public and private spaces for agent communication.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime


class Blackboard:
    """
    Central blackboard for agent communication.
    Maintains public space (visible to all) and private spaces (for specific agent groups).
    """
    
    def __init__(self):
        self.public_space: List[Dict[str, Any]] = []
        self.private_spaces: Dict[str, List[Dict[str, Any]]] = {}
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "round": 0
        }
    
    def add_public_message(self, agent_name: str, content: str, message_type: str = "message", 
                          metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a message to the public space.
        
        Args:
            agent_name: Name of the agent posting the message
            content: Message content
            message_type: Type of message (e.g., "plan", "critique", "solution")
            metadata: Optional additional metadata
        """
        message = {
            "agent": agent_name,
            "content": content,
            "type": message_type,
            "timestamp": datetime.now().isoformat(),
            "round": self.metadata["round"]
        }
        if metadata:
            message.update(metadata)
        self.public_space.append(message)
    
    def add_private_message(self, space_key: str, agent_name: str, content: str,
                           message_type: str = "message", metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a message to a private space.
        
        Args:
            space_key: Key identifying the private space (e.g., "debate_1", "reflection_planner_critic")
            agent_name: Name of the agent posting the message
            content: Message content
            message_type: Type of message
            metadata: Optional additional metadata
        """
        if space_key not in self.private_spaces:
            self.private_spaces[space_key] = []
        
        message = {
            "agent": agent_name,
            "content": content,
            "type": message_type,
            "timestamp": datetime.now().isoformat(),
            "round": self.metadata["round"]
        }
        if metadata:
            message.update(metadata)
        self.private_spaces[space_key].append(message)
    
    def get_public_messages(self, filter_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all public messages, optionally filtered by type.
        
        Args:
            filter_type: Optional message type filter
            
        Returns:
            List of public messages
        """
        if filter_type:
            return [msg for msg in self.public_space if msg.get("type") == filter_type]
        return self.public_space.copy()
    
    def get_private_messages(self, space_key: str) -> List[Dict[str, Any]]:
        """
        Get messages from a specific private space.
        
        Args:
            space_key: Key identifying the private space
            
        Returns:
            List of messages from the private space
        """
        return self.private_spaces.get(space_key, []).copy()
    
    def get_all_messages_summary(self) -> str:
        """
        Get a formatted summary of all public messages for LLM consumption.
        
        Returns:
            Formatted string summary
        """
        if not self.public_space:
            return "The blackboard is empty."
        
        summary_parts = [f"Blackboard State (Round {self.metadata['round']}):\n"]
        for i, msg in enumerate(self.public_space, 1):
            summary_parts.append(
                f"{i}. [{msg['type'].upper()}] {msg['agent']}: {msg['content']}\n"
            )
        return "\n".join(summary_parts)
    
    def increment_round(self) -> None:
        """Increment the current round number."""
        self.metadata["round"] += 1
    
    def create_debate_space(self, agent_names: List[str]) -> str:
        """
        Create a debate space for multiple agents.
        
        Args:
            agent_names: List of agent names participating in the debate
            
        Returns:
            Space key for the debate space
        """
        space_key = f"debate_{'_'.join(sorted(agent_names))}"
        if space_key not in self.private_spaces:
            self.private_spaces[space_key] = []
        return space_key
    
    def create_reflection_space(self, agent_name: str) -> str:
        """
        Create a self-reflection space for an agent.
        
        Args:
            agent_name: Name of the agent for self-reflection
            
        Returns:
            Space key for the reflection space
        """
        space_key = f"reflection_{agent_name}"
        if space_key not in self.private_spaces:
            self.private_spaces[space_key] = []
        return space_key
    
    def get_debate_messages(self, agent_names: List[str]) -> List[Dict[str, Any]]:
        """Get messages from a debate space."""
        space_key = f"debate_{'_'.join(sorted(agent_names))}"
        return self.get_private_messages(space_key)
    
    def get_reflection_messages(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get messages from an agent's reflection space."""
        space_key = f"reflection_{agent_name}"
        return self.get_private_messages(space_key)
    
    def get_all_private_spaces_summary(self) -> str:
        """
        Get a summary of all private spaces (for solution extraction).
        
        Returns:
            Formatted string summary of private spaces
        """
        if not self.private_spaces:
            return "No private spaces."
        
        summary_parts = ["Private Spaces:\n"]
        for space_key, messages in self.private_spaces.items():
            if messages:
                summary_parts.append(f"\n{space_key}:")
                for msg in messages:
                    summary_parts.append(f"  - {msg['agent']}: {msg['content'][:100]}...")
        return "\n".join(summary_parts)
    
    def clear(self) -> None:
        """Clear all messages (use with caution)."""
        self.public_space = []
        self.private_spaces = {}
        self.metadata["round"] = 0

