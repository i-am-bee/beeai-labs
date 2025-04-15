#!/usr/bin/env python3
"""
Agent that uses a CBOM file to identify potential quantum-unsafe cryptography.
Output is a JSON string containing findings.
"""

import json
import time
import asyncio
import sys
import traceback
import tempfile
import os
from typing import Any # Added for templates typing

# BeeAI Framework imports
from beeai_framework.agents.react import ReActAgent, ReActAgentRunOutput
from beeai_framework.backend import ChatModel
from beeai_framework.errors import FrameworkError
from beeai_framework.memory import UnconstrainedMemory
# Removed PythonTool as it's not explicitly used here, can be added back if needed
# from beeai_framework.tools.code import LocalPythonStorage, PythonTool
from beeai_framework.adapters.openai.backend.chat import OpenAIChatModel

# Standard library imports (kept as needed)
import dotenv # Keep if you load env vars from a .env file

# Load environment variables if using a .env file
dotenv.load_dotenv()

def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"

async def run_finder_agent(cbom: dict) -> str: # Changed input type hint to dict, return type kept as str
    """
    Runs the Finder Agent using BeeAI Framework to analyze a CBOM.

    Args:
        cbom: A dictionary representing the CBOM data.

    Returns:
        A string containing the agent's analysis findings.
        (Note: The agent is instructed to return JSON, but this function returns the raw string output).
    """
    print("🐝 Running the Finder Agent...")

    # --- Agent Configuration ---

    # 1. Instructions
    try:
        with open("instructions/instructions_finder.txt", 'r') as instructions_file:
            agent_instructions = instructions_file.read()
    except FileNotFoundError:
        print("Error: instructions/instructions_finder.txt not found.", file=sys.stderr)
        # Provide default instructions or raise a more specific error
        agent_instructions = "You are an AI assistant. Analyze the provided CBOM data to identify potential quantum-unsafe cryptographic components. Respond with your findings in JSON format."
        # Or raise FileNotFoundError("instructions/instructions_finder.txt is required.")

    templates: dict[str, Any] = {
        "system": lambda template: template.update(
            defaults={"instructions": agent_instructions}
        )
    }

    # 2. Model and Connection Settings
    api_key = os.getenv("BEE_API_KEY")
    base_url = os.getenv("BEE_API")
    if not api_key or not base_url:
        raise ValueError("BEE_API_KEY and BEE_API environment variables must be set.")


    model_id = "rits/meta-llama/llama-3-1-70b-instruct"

    settings = {
        # Add specific headers if needed, like in the gitfetcher example
        "extra_headers": { "RITS_API_KEY": api_key},
        "api_key": api_key,
        "base_url": f"{base_url}/v1",
    }

    # 3. Tools (Optional)
    # No specific tools seem required for just analyzing JSON based on the original code
    tools = []
    # Example if PythonTool was needed:
    # code_interpreter_url = os.getenv("CODE_INTERPRETER_URL")
    # if code_interpreter_url:
    #     tools.append(
    #         PythonTool(
    #             code_interpreter_url,
    #             LocalPythonStorage(
    #                 local_working_dir=tempfile.mkdtemp("code_interpreter_source_finder"),
    #                 interpreter_working_dir=os.getenv("CODE_INTERPRETER_TMPDIR", "./tmp/code_interpreter_target_finder"),
    #             ),
    #         )
    #     )

    # 4. Prompt Construction
    # Combine the fixed prompt and the CBOM data into a single input string
    user_prompt = "Am I using any unsafe cryptography in my code? Please analyze the following CBOM data and provide your findings in JSON format."
    cbom_json_string = json.dumps(cbom, indent=4) # Ensure CBOM is a JSON string

    # Display input for debugging/demo purposes
    print(heading(text="Input (prompt, cbom)"))
    print(user_prompt)
    print('---')
    if ((pause := os.environ.get("BEE_DEMOPAUSE")) is not None):
        try:
            time.sleep(int(pause))
        except ValueError:
            print(f"Warning: Invalid BEE_DEMOPAUSE value '{pause}'. Must be an integer.", file=sys.stderr)
    print(cbom_json_string) # Print the JSON string being sent
    if ((pause := os.environ.get("BEE_DEMOPAUSE")) is not None):
        try:
            time.sleep(int(pause))
        except ValueError:
            print(f"Warning: Invalid BEE_DEMOPAUSE value '{pause}'. Must be an integer.", file=sys.stderr)


    # Combine into the final input for the agent
    agent_input = f"{user_prompt}\n\nCBOM Data:\n```json\n{cbom_json_string}\n```"

    # --- Agent Execution ---
    print(heading(text="Run model"))
    llm = OpenAIChatModel(model_id=model_id, settings=settings)
    agent = ReActAgent(llm=llm, templates=templates, tools=tools, memory=UnconstrainedMemory())

    output: ReActAgentRunOutput = await agent.run(agent_input).on(
        "update", lambda data, event: print(f"Agent({data.update.key}) 🤖 : ", data.update.parsed_value)
    )

    # --- Result Handling ---
    answer = output.result.text
    print(heading(text="Answer"))
    print(answer)

    # No explicit cleanup needed for ReActAgent (unlike OpenAI Assistants/Threads)

    # TODO: The original function hint was -> json. The agent is asked for JSON.
    # Consider adding JSON parsing here if the caller expects a dict/list.
    # try:
    #     parsed_answer = json.loads(answer)
    #     return parsed_answer # Or return the string `answer` if raw text is preferred
    # except json.JSONDecodeError:
    #     print("Warning: Agent output was not valid JSON.", file=sys.stderr)
    #     return answer # Return raw string on parsing failure

    return answer # Return the raw string output for now

# --- Main Execution Block ---
if __name__ == "__main__":
    # Load the CBOM data
    cbom_file_path = 'data/Mastercard-client-encryption-java.cbom'
    try:
        with open(cbom_file_path, 'r') as c:
            # Load CBOM as a Python dictionary
            cbom_data = json.load(c)
    except FileNotFoundError:
        print(f"Error: CBOM file not found at {cbom_file_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not parse JSON from {cbom_file_path}", file=sys.stderr)
        sys.exit(1)

    # Run the agent asynchronously
    try:
        # Use asyncio.run() to execute the async function
        findings_str = asyncio.run(run_finder_agent(cbom_data))
        print("\n" + "="*80)
        print("Finder Agent Finished. Result:")
        print(findings_str)
        # Optionally, try parsing the result if JSON is expected
        # try:
        #    findings_json = json.loads(findings_str)
        #    print("\nParsed Findings (JSON):")
        #    print(json.dumps(findings_json, indent=4))
        # except json.JSONDecodeError:
        #    print("\nNote: The final output could not be parsed as JSON.")

    except FrameworkError as e:
        print("\nAn error occurred within the BeeAI Framework:", file=sys.stderr)
        traceback.print_exc()
        # sys.exit(e.explain()) # Use explain() if available and helpful
        sys.exit(1)
    except ValueError as e:
        print(f"\nConfiguration Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print("\nAn unexpected error occurred:", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)