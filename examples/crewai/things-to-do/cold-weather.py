#!/usr/bin/env python

from crewai import Agent, Crew, Task, Process, LLM
from crewai.project import CrewBase, agent, task, crew
from crewai.tools import tool
from langchain_community.chat_models import ChatOllama

# Many ways of using tools - varient of the langchain version
# Also using duckduckgo for now but the langchain tool version
from langchain_community.tools import DuckDuckGoSearchRun

@CrewBase
class ColdWeatherCrew:
    """Crew to find activities to do in cold or wet weather"""
    
    # setup LLM
    llm = LLM(model="ollama/llama3.1",base_url="http://localhost:11434")
   
    # Use the duckduckgo search tool
    @tool("DuckDuckGo")
    def ddg_search(question: str) -> str:
        """Performs a web search using the DuckDuckGo search engine"""
        search_tool = DuckDuckGoSearchRun()
        return search_tool.run(question)

    @agent
    def activityplanner(self) -> Agent:
        return Agent(
            config=self.agents_config['activityplanner'],
            tools=[self.ddg_search],  # Include the DuckDuckGo search tool
            # Hardcode to ollama 3.1 running locally
            llm=self.llm,
            verbose = True
        )

    # Simple task to provide a list of activities
    @task
    def activityfinder_task(self) -> Task:
        return Task(
            config=self.tasks_config['activityfinder_task'],
            verbose=True
        )

    # Create a crew with a sequential process (basic case as only one task)
    @crew
    def activitycrew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )

if __name__ == "__main__":
    print("Running crew...")
    inputs = {"location": "San Francisco"}
    ColdWeatherCrew().activitycrew().kickoff(inputs=inputs)