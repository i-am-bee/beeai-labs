import sys

from dotenv import load_dotenv

from bee_agent import BeeAgent, LLM


LLMS = {
    "ollama": "ollama/llama3.1",
    "openai": "openai/gpt-4o-mini",
    "watsonx": "watsonx/ibm/granite-3-8b-instruct",
}

HELP = """
Usage:
  examples.bee_agent.llms <ollama|openai|watsonx>
Arguments
  `ollama` - requires local ollama service running (i.e., http://127.0.0.1:11434)
  `openai` - requires  environment variable
      - OPENAI_API_KEY: API key
  `watsonx` - requires environment variable
      - WATSONX_URL - base URL of your WatsonX instance
    and one of the following
      - WATSONX_APIKEY: API key
      - WATSONX_TOKEN: auth token
"""


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(HELP)
    elif sys.argv[1] == "--help":
        print(HELP)
    else:
        load_dotenv()
        model = LLMS.get(sys.argv[1])
        if model:
            agent = BeeAgent(llm=LLM(model=model))
            agent.run("What is the smallest of the Cabo Verde islands?")
        else:
            print(f"Unknown provider: {sys.argv[1]}\n{HELP}")
