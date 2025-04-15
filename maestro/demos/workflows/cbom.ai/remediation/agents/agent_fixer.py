#!/usr/bin/env python3
"""
Agent that uses a findings file (JSON string) to remediate source code
by generating a git patchfile using BeeAI Framework.
Output is a string expected to contain a git patch.
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
# Import PythonTool and its dependencies
from beeai_framework.tools.code import LocalPythonStorage, PythonTool
from beeai_framework.adapters.openai.backend.chat import OpenAIChatModel

# Standard library imports (kept as needed)
import dotenv # Keep if you load env vars from a .env file
# Removed unused imports like warnings, datetime, pprint, Literal, openai

# Load environment variables if using a .env file
dotenv.load_dotenv()

def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"

# Note: Changed input type hint from 'json' (not a standard type hint) to 'str'
async def run_fixer_agent(findings: str) -> str:
    """
    Runs the Fixer Agent using BeeAI Framework to generate a patch file.

    Args:
        findings: A string containing the findings report (expected to be JSON formatted).

    Returns:
        A string containing the agent's generated patch file content.
    """
    print("🐝 Running the Fixer Agent...")

    # --- Agent Configuration ---

    # 1. Instructions
    try:
        with open("instructions/instructions_fixer.txt", 'r') as instructions_file:
            # Instructions should guide the agent on how to use the PythonTool
            # to achieve the goal based on the findings.
            agent_instructions = instructions_file.read()
    except FileNotFoundError:
        print("Error: instructions/instructions_fixer.txt not found.", file=sys.stderr)
        # Provide default instructions or raise a more specific error
        agent_instructions = """You are an AI assistant specialized in code remediation.
You will be given a findings report (in JSON format) detailing security vulnerabilities or necessary code changes.
Your task is to generate a git patch file that fixes the identified issues in the relevant source code.
Use the provided Python code execution tool to:
1. Clone the relevant repository (information likely in findings or prompt).
2. Analyze the findings and locate the code sections to modify.
3. Apply the necessary changes to the code.
4. Generate a git diff (patch file) representing these changes.
5. Output *only* the raw git patch content, enclosed in ```diff ... ``` markers.
You have access to a GitHub token provided in the prompt for repository interactions.
Ensure the patch is correctly formatted."""
        # Or raise FileNotFoundError("instructions/instructions_fixer.txt is required.")

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

    # Decide on model based on environment variables (same logic as original)
    backend = os.getenv("LLM_BACKEND", "bam") # Default to 'bam' if not set
    if backend == "bam":
        # Using the specific model from agent_finder2.py example
        model_id = os.getenv("BAM_MODEL", "rits/meta-llama/llama-3-1-70b-instruct")
    elif backend == "ollama":
        model_id = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    else:
        print(f"Warning: Unsupported LLM_BACKEND '{backend}'. Defaulting to BAM model.", file=sys.stderr)
        model_id = "rits/meta-llama/llama-3-1-70b-instruct"

    settings = {
        # Add specific headers if needed, like in the gitfetcher example
        "extra_headers": { "RITS_API_KEY": api_key}, # Assuming this header is needed
        "api_key": api_key,
        "base_url": f"{base_url}/v1",
    }

    # 3. Tools - Use PythonTool for code execution
    tools = []
    code_interpreter_url = os.getenv("CODE_INTERPRETER_URL", "http://localhost:50081") # Default URL
    if code_interpreter_url:
        # Create unique temp directories for this agent
        local_dir = tempfile.mkdtemp("code_interpreter_source_fixer")
        target_dir = os.getenv("CODE_INTERPRETER_TMPDIR", "./tmp/code_interpreter_target_fixer")
        print(f"Code Interpreter Local Dir: {local_dir}")
        print(f"Code Interpreter Target Dir: {target_dir}")
        tools.append(
            PythonTool(
                code_interpreter_url,
                LocalPythonStorage(
                    local_working_dir=local_dir,
                    interpreter_working_dir=target_dir,
                ),
            )
        )
    else:
        print("Warning: CODE_INTERPRETER_URL not set. PythonTool will not be available.", file=sys.stderr)


    # 4. Prompt Construction
    gh_token = os.environ.get("GH_TOKEN")
    if not gh_token:
        print("Warning: GH_TOKEN environment variable not set. Agent may not be able to interact with GitHub.", file=sys.stderr)
        # Decide if this is a fatal error or just a warning
        # raise ValueError("GH_TOKEN environment variable must be set.")

    # Combine the fixed prompt and the findings data into a single input string
    user_prompt = f"Fix my code based on the findings report provided below. Use the GitHub API token '{gh_token}' if needed for repository access."

    # Display input for debugging/demo purposes
    print(heading(text="Input (prompt, findings)"))
    print(user_prompt)
    print('---')
    if ((pause := os.environ.get("BEE_DEMOPAUSE")) is not None):
        try:
            time.sleep(int(pause))
        except ValueError:
            print(f"Warning: Invalid BEE_DEMOPAUSE value '{pause}'. Must be an integer.", file=sys.stderr)
    # Assume findings is a string, potentially large JSON
    print(findings)
    if ((pause := os.environ.get("BEE_DEMOPAUSE")) is not None):
        try:
            time.sleep(int(pause))
        except ValueError:
            print(f"Warning: Invalid BEE_DEMOPAUSE value '{pause}'. Must be an integer.", file=sys.stderr)

    # Combine into the final input for the agent
    # Use markdown code block for clarity if findings is JSON
    agent_input = f"{user_prompt}\n\nFindings Report:\n```json\n{findings}\n```"

    # --- Agent Execution ---
    print(heading(text="Run model"))
    llm = OpenAIChatModel(model_id=model_id, settings=settings)
    # Pass the PythonTool instance to the agent
    agent = ReActAgent(llm=llm, templates=templates, tools=tools, memory=UnconstrainedMemory())

    output: ReActAgentRunOutput = await agent.run(agent_input).on(
        "update", lambda data, event: print(f"Agent({data.update.key}) 🤖 : ", data.update.parsed_value)
    )

    # --- Result Handling ---
    answer = output.result.text
    print(heading(text="Answer"))
    print(answer) # The raw output, expected to be the patch

    # No explicit cleanup needed for ReActAgent or tools managed by it

    # Optional: Extract content within ```diff ... ``` if needed by caller
    # match = re.search(r'```diff\n(.*?)\n```', answer, re.DOTALL)
    # if match:
    #     return match.group(1)
    # else:
    #     print("Warning: Could not extract diff block from agent output.", file=sys.stderr)
    #     return answer # Return raw answer if extraction fails

    return answer # Return the raw string output

# --- Main Execution Block ---
if __name__ == "__main__":
    # Load the findings data (assuming it's a JSON string in the file)
    findings_file_path = 'data/findings.json'
    try:
        with open(findings_file_path, 'r') as f:
            findings_str = f.read() # Read the whole file as a string
    except FileNotFoundError:
        print(f"Error: Findings file not found at {findings_file_path}", file=sys.stderr)
        sys.exit(1)

    # Run the agent asynchronously
    try:
        # Use asyncio.run() to execute the async function
        patch_str = asyncio.run(run_fixer_agent(findings_str))
        print("\n" + "="*80)
        print("Fixer Agent Finished. Result (Patch Content):")
        print(patch_str)

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