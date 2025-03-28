# SPDX-License-Identifier: Apache-2.0
from enum import Enum
from typing import Callable, Type, Union

from .bee_agent import BeeAgent
from .crewai_agent import CrewAIAgent

class AgentFramework(Enum):
    """Enumeration of supported frameworks"""
    BEE = "bee"
    CREWAI = "crewai"
    MOCK = "mock"

    """Enumeration of supported frameworks"""
    FRAMEWORKS = {
        'BEEAI': "beeai",
        'CREWAI': "crewai",
        'MOCK': "mock",

        # Not yet supported but adding in anticipation
        'LANGFLOW': "langflow",
        'OPENAI': "openai",
        'REMOTE': "remote"   
    }

    EMOJIS = {
        'BEEAI': '🐝',
        'CREWAI': '👥',
        'LANGFLOW': '⛓',
        'OPENAI': '🔓',
        'MOCK': '🤖',
        'REMOTE': '💸'
    }

class AgentFactory:
    """Factory class for handling agent frameworks"""
    @staticmethod
    def create_agent(framework: AgentFramework) -> Callable[..., Union[BeeAgent, CrewAIAgent]]:
        """Create an instance of the specified agent framework.

        Args:
            framework (AgentFramework): The framework to create. Must be a valid enum value.

        Returns:
            A new instance of the corresponding agent class.
        """
        factories = {
            AgentFramework.BEE: BeeAgent,
            AgentFramework.CREWAI: CrewAIAgent
        }

        if framework not in factories:
            raise ValueError(f"Unknown framework: {framework}")
        
        return factories[framework]

    @classmethod
    def get_factory(cls, framework: str) -> Callable[..., Union[BeeAgent, CrewAIAgent]]:
        """Get a factory function for the specified agent type."""
        return cls.create_agent(framework)
