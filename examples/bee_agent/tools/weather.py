from bee_agent import BeeAgent, LLM
from bee_agent.tools import WeatherTool

agent = BeeAgent(llm=LLM(model="llama3.1"), tools=[WeatherTool()])

agent.run("What's the current weather in Las Vegas?")
