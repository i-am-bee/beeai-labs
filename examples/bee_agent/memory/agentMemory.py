from bee_agent import BeeAgent, LLM
from bee_agent.memory import UnconstrainedMemory, BaseMessage
from bee_agent.memory.message import Role
from bee_agent.llms.prompt import Prompt
import asyncio

# Initialize the memory and LLM
memory = UnconstrainedMemory()

llm = LLM(
    model="llama3.2",  # or whatever model you're using
    base_url="http://localhost:11434",
)

# Initialize the agent
agent = BeeAgent(llm=llm, memory=memory, tools=[])


async def main():
    try:
        # Create user message
        user_input = "Hello world!"
        user_message = BaseMessage(role=Role.USER, text=user_input)

        # Await adding user message to memory
        await memory.add(user_message)
        print("Added user message to memory")

        # Create and run the prompt (synchronously)
        prompt: Prompt = {"prompt": user_input}
        # No await here since run() is not async
        response = agent.run(prompt)
        print(f"Received response: {response}")

        # Get the actual text from the ChatLLMOutput
        response_text = (
            response.output.response if hasattr(response, "output") else str(response)
        )

        # Create and store assistant's response
        assistant_message = BaseMessage(role=Role.ASSISTANT, text=response_text)

        # Await adding assistant message to memory
        await memory.add(assistant_message)
        print("Added assistant message to memory")

        # Print results
        print(f"\nMessages in memory: {len(agent.memory.messages)}")

        if len(agent.memory.messages) >= 1:
            user_msg = agent.memory.messages[0]
            print(f"User: {user_msg.text}")

        if len(agent.memory.messages) >= 2:
            agent_msg = agent.memory.messages[1]
            print(f"Agent: {agent_msg.text}")
        else:
            print("No agent message found in memory")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback

        print(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(main())
