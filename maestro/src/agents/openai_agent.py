from .agent import Agent

class OpenAIAgent(Agent):
    def __init__(self, agent: dict) -> None:
        super.__init__(agent)
    
    async def run(self, prompt: str) -> str:
        """
        Runs the agent with the given prompt.
        Args:
            prompt (str): The prompt to run the agent with.
        """
        self.print(f"Running {self.agent_name}...")
        answer = f"answer for {prompt}" 
        self.print(f"Response from {self.agent_name}: {answer}")
        return answer

    async def run_streaming(self, prompt: str) -> str:
        """
        Runs the agent in streaming mode with the given prompt.
        Args:
            prompt (str): The prompt to run the agent with.
        """
        return self.run(prompt)