#!/usr/bin/env python3
"""
Agent that applies a patch to a source repository and generates a PR
using BeeAI Framework.
Output is a str specifying the URL of the generated PR (or an error message).
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

async def run_patcher_agent(repo: str, patch: str) -> str:
    """
    Runs the Patcher Agent using BeeAI Framework to apply a patch and create a PR.

    Args:
        repo: The URL of the target GitHub repository.
        patch: A string containing the git patch content.

    Returns:
        A string containing the URL of the created Pull Request or an error message.
    """
    print("🐝 Running the Patcher Agent...")

    # --- Agent Configuration ---

    # 1. Instructions
    try:
        with open("instructions/instructions_patcher.txt", 'r') as instructions_file:
            # Instructions must guide the agent on using PythonTool for git operations and PR creation
            agent_instructions = instructions_file.read()
    except FileNotFoundError:
        print("Error: instructions/instructions_patcher.txt not found.", file=sys.stderr)
        # Provide default instructions or raise a more specific error
        agent_instructions = """You are an AI assistant specialized in automating code deployment via GitHub.
You will be given a target GitHub repository URL, a git patch, and a GitHub API token.
Your task is to apply the patch to the repository and create a Pull Request (PR) with the changes.
Use the provided Python code execution tool to perform the following steps:
1. Configure git with necessary user details (you can use generic ones like 'AI Patcher Bot').
2. Clone the specified repository using the provided GitHub token for authentication if necessary.
3. Create a new unique branch (e.g., 'ai-patch-<timestamp>').
4. Apply the provided patch content to the cloned repository (e.g., using `git apply`). Handle potential patch application errors.
5. Add the changes, commit them with a descriptive message (e.g., 'Apply AI-generated patch').
6. Push the new branch to the origin repository using the GitHub token.
7. Use the GitHub API (e.g., via the `requests` library or a dedicated GitHub library like `PyGithub` if available in the execution environment) and the provided token to create a Pull Request from the newly pushed branch to the repository's default branch (usually 'main' or 'master'). Include a suitable title and body for the PR.
8. Output *only* the URL of the successfully created Pull Request. If any step fails, output a clear error message explaining the failure.
Ensure you correctly use the provided GitHub token for all authenticated operations (cloning, pushing, API calls)."""
        # Or raise FileNotFoundError("instructions/instructions_patcher.txt is required.")

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

    # Decide on model based on environment variables (consistent with other agents)
    backend = os.getenv("LLM_BACKEND", "bam") # Default to 'bam' if not set
    if backend == "bam":
        model_id = os.getenv("BAM_MODEL", "rits/meta-llama/llama-3-1-70b-instruct")
    elif backend == "ollama":
        model_id = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    else:
        print(f"Warning: Unsupported LLM_BACKEND '{backend}'. Defaulting to BAM model.", file=sys.stderr)
        model_id = "rits/meta-llama/llama-3-1-70b-instruct"

    settings = {
        "extra_headers": { "RITS_API_KEY": api_key}, # Assuming this header is needed
        "api_key": api_key,
        "base_url": f"{base_url}/v1",
    }

    # 3. Tools - Use PythonTool for code execution (git, GitHub API calls)
    tools = []
    code_interpreter_url = os.getenv("CODE_INTERPRETER_URL", "http://localhost:50081") # Default URL
    if code_interpreter_url:
        # Create unique temp directories for this agent
        local_dir = tempfile.mkdtemp("code_interpreter_source_patcher")
        target_dir = os.getenv("CODE_INTERPRETER_TMPDIR", "./tmp/code_interpreter_target_patcher")
        print(f"Code Interpreter Local Dir: {local_dir}")
        print(f"Code Interpreter Target Dir: {target_dir}")
        tools.append(
            PythonTool(
                code_interpreter_url,
                LocalPythonStorage(
                    local_working_dir=local_dir,
                    interpreter_working_dir=target_dir,
                ),
                # You might need to specify allowed modules if the interpreter is restricted
                # allowed_modules=["git", "requests", "os", "subprocess", "shutil"]
            )
        )
    else:
        print("Warning: CODE_INTERPRETER_URL not set. PythonTool will not be available.", file=sys.stderr)
        # This agent likely *requires* the PythonTool, so maybe raise an error?
        # raise ValueError("CODE_INTERPRETER_URL must be set for the Patcher Agent.")


    # 4. Prompt Construction
    gh_token = os.environ.get("GH_TOKEN")
    if not gh_token:
        # This agent absolutely needs the token
        raise ValueError("GH_TOKEN environment variable must be set for the Patcher Agent.")

    # Combine the fixed prompt, repo URL, patch, and token into a single input string
    user_prompt = f"Using the patch provided below, create a pull request for the code at {repo}. Use the GitHub API token '{gh_token}' for all necessary operations (cloning, pushing, creating PR)."

    # Display input for debugging/demo purposes
    print(heading(text="Input (prompt, patch)"))
    print(user_prompt)
    print('---')
    if ((pause := os.environ.get("BEE_DEMOPAUSE")) is not None):
        try:
            time.sleep(int(pause))
        except ValueError:
            print(f"Warning: Invalid BEE_DEMOPAUSE value '{pause}'. Must be an integer.", file=sys.stderr)
    # Assume patch is a string, potentially large
    print("Patch Content:")
    print(patch)
    if ((pause := os.environ.get("BEE_DEMOPAUSE")) is not None):
        try:
            time.sleep(int(pause))
        except ValueError:
            print(f"Warning: Invalid BEE_DEMOPAUSE value '{pause}'. Must be an integer.", file=sys.stderr)

    # Combine into the final input for the agent
    # Use markdown code block for the patch
    agent_input = f"{user_prompt}\n\nPatch Content:\n```diff\n{patch}\n```"

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
    print(answer) # The raw output, expected to be the PR URL or an error message

    # No explicit cleanup needed for ReActAgent or tools managed by it

    return answer # Return the raw string output

# --- Main Execution Block ---
if __name__ == "__main__":
    # Define the target repository
    repo_url = 'https://github.com/planetf1/client-encryption-java' # Example repo

    # Load the patch data
    patch_file_path = 'data/patchfile'
    try:
        with open(patch_file_path, 'r') as f:
            patch_content = f.read() # Read the whole file as a string
    except FileNotFoundError:
        print(f"Error: Patch file not found at {patch_file_path}", file=sys.stderr)
        sys.exit(1)

    # Run the agent asynchronously
    try:
        # Use asyncio.run() to execute the async function
        result_str = asyncio.run(run_patcher_agent(repo_url, patch_content))
        print("\n" + "="*80)
        print("Patcher Agent Finished. Result:")
        print(result_str) # Should be the PR URL or an error

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