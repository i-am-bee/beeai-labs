from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic, Union
from dataclasses import dataclass
import re

from litellm import completion
import math


from .base_output import BaseChatLLMOutput
from .output import ChatLLMOutput, ChatOutput
from .prompt import Prompt
from bee_agent.memory.base_memory import BaseMemory, BaseMessage
from bee_agent.utils.custom_logger import BeeLogger
from bee_agent.utils.roles import Role


T = TypeVar("T", bound="BaseChatLLMOutput")
logger = BeeLogger(__name__)


class BaseLLM(Generic[T], ABC):
    """Abstract base class for Language Model implementations."""

    base_url: Optional[str]
    model: Optional[str]

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_url = base_url

        if "/" not in model:
            self.model = f"ollama_chat/{model}"
        else:
            self.model = (
                model
                if not model.startswith("ollama/")
                else f"{model.replace('ollama/', 'ollama_chat/')}"
            )

    @abstractmethod
    def inference(self, input: List[BaseMessage], options: Any) -> T:
        pass

    @abstractmethod
    def parse_output(self, output, tools):
        pass

    def generate(self, prompt: Union[Prompt, List[BaseMessage]], options=None) -> T:
        if type(prompt) is dict:
            input = [BaseMessage.of({"role": Role.USER, "text": prompt.get("prompt")})]
        else:
            input = prompt

        answer = self.inference(input, options)
        return answer

    @abstractmethod
    def tokenize(self, input: str) -> T:
        pass


class LLM(BaseLLM[BaseChatLLMOutput]):
    parameters: Dict[str, Any] = {}
    chat_endpoint = "/api/chat"

    def __init__(
        self,
        model: str = "ollama_chat/llama3.1",
        base_url: str = "http://localhost:11434",
        parameters: Dict[str, Any] = {},
    ):
        h = base_url[:-1] if base_url.endswith("/") else base_url
        self.parameters = {
            "temperature": 0,
            "repeat_penalty": 1.0,
            "num_predict": 2048,
        } | parameters

        super().__init__(h, model)

    def prepare_messages(self, input: List[BaseMessage]):
        return list(map(lambda x: {"role": x.role, "content": x.text}, input))

    def inference(self, input: List[BaseMessage], options=None) -> BaseChatLLMOutput:
        response = completion(
            model=self.model,
            messages=self.prepare_messages(input),
        )

        logger.debug(f"Inference response choices size: {len(response.choices)}")
        response_content = (
            response.get("choices", [{}])[0].get("message", {}).get("content", "")
        )
        logger.debug(f"Inference response content:\n{response_content}")

        return ChatLLMOutput(output=ChatOutput(response=response_content))

    def tokenize(self, input: str) -> T:
        return {"tokens_count": math.ceil(len(input) / 4)}

    def parse_output(self, output, tools):
        if len(tools):
            regex = (
                r"Thought: .+\n+(?:Final Answer: [\s\S]+|Function Name: ("
                + "|".join(list(map(lambda x: x.name, tools)))
                + ")\n+Function Input: \\{.*\\}(\n+Function Output:)?)"
            )
        else:
            regex = r"Thought: .+\n+Final Answer: [\s\S]+"
        r = re.search(regex, output.text)
        if r is not None:
            return r.group()


@dataclass
class AgentInput(Generic[T]):
    """Input configuration for agent initialization."""

    llm: BaseLLM[T]
    memory: "BaseMemory"
