from abc import ABC, abstractmethod


class BaseRunner(ABC):
    _llm = None
    tools = []
    iterations = []

    def __init__(self, llm, tools=[], options=None):
        self._llm = llm
        self.tools = tools

    @abstractmethod
    def init_memory(self, input):
        pass

    @abstractmethod
    def iterate(self):
        pass

    def start_iteration(self):
        pass
