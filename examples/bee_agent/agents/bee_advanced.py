# SPDX-License-Identifier: Apache-2.0

import json
from dotenv import load_dotenv
import asyncio
from typing import Dict, Any
import logging
import signal

from bee_agent.agents import BeeAgent
from bee_agent.memory import UnconstrainedMemory
from bee_agent.utils import BeeLogger, BeeEventEmitter, MessageEvent
from bee_agent.llms import LLM
from bee_agent.tools import WeatherTool, Tool

# Load environment variables
load_dotenv()

# Configure logging
logger = BeeLogger("app", level=logging.DEBUG)
event_emitter = BeeEventEmitter()


class DuckDuckGoSearchType:
    STRICT = "STRICT"
    MODERATE = "MODERATE"
    OFF = "OFF"


class DuckDuckGoSearchTool(Tool):
    """DuckDuckGo search tool implementation"""

    name = "DuckDuckGoSearch"
    description = "Search for information on the web using DuckDuckGo"

    def __init__(
        self, max_results: int = 10, safe_search: str = DuckDuckGoSearchType.STRICT
    ):
        super().__init__()
        self.max_results = max_results
        self.safe_search = safe_search

    def input_schema(self):
        return """
        {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                }
            },
            "required": ["query"]
        }
        """

    def _run(self, input: Dict[str, Any], options=None):
        try:
            # Ensure input is properly formatted
            if isinstance(input, str):
                input = json.loads(input)

            query = input.get("query", "")

            if not query:
                return "Error: No search query provided"

            # Here you would implement the actual DuckDuckGo search
            # For now, return a mock response
            return {
                "results": [
                    {
                        "title": f"Search result for: {query}",
                        "link": "https://example.com",
                        "snippet": f"This is a mock search result for the query: {query}",
                    }
                ],
                "total": 1,
            }
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            return f"Error parsing search input: {str(e)}"
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return f"Error performing search: {str(e)}"


def create_agent() -> BeeAgent:
    """Create and configure the agent with custom tools and prompts"""

    # Initialize LLM
    llm = LLM(
        model="llama3.1",
        parameters={
            "temperature": 0,
            "repeat_penalty": 1.0,
            "num_predict": 2048,
        },
    )

    # Configure tools
    tools = [
        DuckDuckGoSearchTool(max_results=10, safe_search=DuckDuckGoSearchType.STRICT),
        WeatherTool(),
    ]

    # Create agent with custom configuration
    agent = BeeAgent(llm=llm, tools=tools, memory=UnconstrainedMemory())

    return agent


async def handle_tool_response(response: Any, tool_name: str):
    """Handle tool response and emit appropriate events"""
    try:
        if isinstance(response, (dict, list)):
            response_str = json.dumps(response, ensure_ascii=False, indent=2)
        else:
            response_str = str(response)

        event_emitter.emit(
            MessageEvent(
                source="Agent", message=response_str, state=f"tool_response_{tool_name}"
            )
        )

        return response_str
    except Exception as e:
        logger.error(f"Error handling tool response: {str(e)}")
        event_emitter.emit(MessageEvent(source="Agent", message=str(e), state="error"))
        return str(e)


async def run_agent():
    """Main function to run the agent"""

    try:
        # Create agent
        agent = create_agent()
        print(
            "Agent initialized with custom tools and prompts. Type 'exit' or 'quit' to end."
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

                # Emit user message event
                event_emitter.emit(MessageEvent(source="User", message=prompt))

                # Run agent with timeout
                try:
                    # Set timeout signal
                    signal.alarm(120)  # 2 minutes timeout

                    result = agent.run(
                        prompt=prompt,
                        options={
                            "execution": {
                                "max_retries_per_step": 3,
                                "total_max_retries": 10,
                                "max_iterations": 20,
                            }
                        },
                    )

                    # Handle final response
                    if result:
                        event_emitter.emit(
                            MessageEvent(
                                source="Agent",
                                message=str(result),
                                state="final_answer",
                            )
                        )

                finally:
                    # Clear timeout
                    signal.alarm(0)

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {str(e)}")
                event_emitter.emit(
                    MessageEvent(
                        source="Agent",
                        message=f"Error parsing JSON: {str(e)}",
                        state="error",
                    )
                )
            except Exception as e:
                logger.error(f"Error processing prompt: {str(e)}")
                event_emitter.emit(
                    MessageEvent(source="Agent", message=str(e), state="error")
                )

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        event_emitter.emit(MessageEvent(source="Agent", message=str(e), state="error"))


if __name__ == "__main__":
    # Run the async main function
    # logging.basicConfig(level=logging.DEBUG)
    asyncio.run(run_agent())
