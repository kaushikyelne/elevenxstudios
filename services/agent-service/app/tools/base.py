from abc import ABC, abstractmethod
from typing import Any, Dict


class AgentTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the tool as seen by the LLM."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """A detailed description of what the tool does."""
        pass

    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """JSON Schema represention of the tool's parameters."""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """The actual implementation of the tool logic."""
        pass

    def to_gemini_tool(self) -> Dict[str, Any]:
        """Converts the tool definition to Gemini's function declaration format."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }
