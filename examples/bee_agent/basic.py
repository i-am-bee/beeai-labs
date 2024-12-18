from bee_agent import BeeAgent, LLM

agent = BeeAgent(llm=LLM())

agent.run("What is the capital of Massachusetts")
