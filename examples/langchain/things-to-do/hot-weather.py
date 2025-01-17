#!/usr/bin/env python

# Hot weather agent - look for things to do
# pip install langchain_ollama langchain_core langchain_community duckduckgo-search

from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent, Tool, AgentExecutor
from langchain_ollama.chat_models import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun
import os

# Some tools are already known  -in which case ref by name and
# 'from langchain_community.agent_toolkits.load_tools import load_tools'
search = DuckDuckGoSearchRun()
tools = [
    Tool(
        name = "DuckDuckGo Search",
        func=search.run,
        description="useful for when you need to answer questions about current events"
    )
]

# Assume llama3.1 (running locally given env above)
os.environ["LLAMAFILE_SERVER_BASE_URL"] = "http://localhost:11434"
llm = ChatOllama(model="llama3.1", tools=tools)

# This is the input composed from the previous agent. Expect to find
# location. Hardcoded for now
question = "Provide a list of 5 activities to do in the hot weather in San Francisco"

# this is a prompt template which many examples use - but we could explicitly define our own if needed
# In this case it's using a react style approach which iterates to get a good result
prompt = hub.pull("hwchase17/react")

# create the agent & executor (not using any memory)
agent = create_react_agent(llm, prompt=prompt,tools=tools)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True,handle_parsing_errors=False)

# run the agent
result=agent_executor.invoke({"input": question})

print(result["output"])