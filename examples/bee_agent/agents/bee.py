# SPDX-License-Identifier: Apache-2.0

import os
from dotenv import load_dotenv
import asyncio
from typing import Dict, Any
import logging

from bee_agent.agents import BeeAgent
from bee_agent.memory import TokenMemory
from bee_agent.utils import BeeLogger
from bee_agent.llms import LLM
from bee_agent.tools import Tool

# Import LangChain's Wikipedia tool from community package
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# Load environment variables
load_dotenv()

# Configure logging - using DEBUG instead of trace
logger = BeeLogger("app", level=logging.DEBUG)


def get_env_var(key: str, default: str = None) -> str:
    """Helper function to get environment variables with defaults"""
    return os.getenv(key, default)


class LangChainWikipediaTool(Tool):
    """Adapter class to integrate LangChain's Wikipedia tool with our framework"""

    name = "Wikipedia"
    description = (
        "Search factual and historical information from Wikipedia about given topics."
    )

    def __init__(self):
        super().__init__()
        wikipedia = WikipediaAPIWrapper()
        self.wikipedia = WikipediaQueryRun(api_wrapper=wikipedia)

    def input_schema(self):
        return """{
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The topic or question to search for on Wikipedia",
                }
            },
            "required": ["query"],
        }"""

    def _run(self, input: Dict[str, Any], options=None):
        query = input.get("query", "")
        try:
            result = self.wikipedia.run(query)
            return result
        except Exception as e:
            logger.error(f"Wikipedia search error: {str(e)}")
            return f"Error searching Wikipedia: {str(e)}"


def create_agent() -> BeeAgent:
    """Create and configure the agent with tools and LLM"""

    # Initialize LLM
    llm = LLM(
        model="llama3.1",  # Use llama3.1 for better performance
        parameters={
            "temperature": 0,
            "repeat_penalty": 1.0,
            "num_predict": 2048,
        },
    )

    # Configure tools with LangChain's Wikipedia tool
    # tools = [LangChainWikipediaTool(), WeatherTool()]
    tools = [LangChainWikipediaTool()]

    # Add code interpreter tool if URL is configured
    code_interpreter_url = get_env_var("CODE_INTERPRETER_URL")
    if code_interpreter_url:
        # Note: Python tool implementation would go here
        pass

    # Create agent with memory and tools
    agent = BeeAgent(llm=llm, tools=tools, memory=TokenMemory(llm))

    return agent


async def process_agent_events(
    event_data: Dict[str, Any], metadata: Dict[str, Any]
) -> None:
    """Process agent events and log appropriately"""

    if event_data.get("error"):
        logger.error(f"Agent error: {event_data['error']}")

    if event_data.get("retry"):
        logger.info("Agent: retrying the action...")

    if event_data.get("update"):
        update = event_data["update"]
        logger.info(f"Agent ({update.get('key')}): {update.get('value')}")


async def main():
    """Main application loop"""

    try:
        # Create agent
        agent = create_agent()

        # Print code interpreter status if configured
        code_interpreter_url = get_env_var("CODE_INTERPRETER_URL")
        if code_interpreter_url:
            print(
                f"🛠️ System: The code interpreter tool is enabled. Please ensure that it is running on {code_interpreter_url}"
            )

        print(
            "Agent initialized with LangChain Wikipedia tool. Type 'exit' or 'quit' to end."
        )

        # Main interaction loop
        while True:
            try:
                # Get user input
                prompt = input("\nUser: ").strip()
                if not prompt:
                    continue

                if prompt.lower() in ["exit", "quit"]:
                    break
                print(">>>", prompt)
                # Run agent with the prompt
                agent.run(
                    prompt=prompt,
                    options={
                        "execution": {
                            "max_retries_per_step": 3,
                            "total_max_retries": 10,
                            "max_iterations": 20,
                        }
                    },
                )

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                logger.error(f"Error processing prompt: {str(e)}")

    except Exception as e:
        logger.error(f"Application error: {str(e)}")


if __name__ == "__main__":
    # Run the async main function
    # logging.basicConfig(level=logging.DEBUG)

    asyncio.run(main())
