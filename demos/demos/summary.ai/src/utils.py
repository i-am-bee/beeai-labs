import json
import os
import dotenv
from openai import OpenAI

dotenv.load_dotenv()

def load_agent(agent_name):
    """Loads agent ID from agent_store.json."""
    with open("agent_store.json") as f:
        agent_store = json.load(f)
    return agent_store.get(agent_name)

def run_agent(agent_name, prompt):
    """Executes an agent with given input and returns the response."""
    print(f"🐝 Running {agent_name}...")

    agent_id = load_agent(agent_name)
    if not agent_id:
        raise ValueError(f"Agent {agent_name} not found in agent_store.json")

    client = OpenAI(
        base_url=f'{os.getenv("BEE_API")}/v1',
        api_key=os.getenv("BEE_API_KEY"),
    )

    assistant = client.beta.assistants.retrieve(agent_id)
    thread = client.beta.threads.create(
        messages=[{"role": "user", "content": str(prompt)}]
    )
    client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=assistant.id
    )

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    answer = messages.data[0].content[0].text.value
    print(f"🐝 Response from {agent_name}: {answer}")
    return answer
