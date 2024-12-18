from bee_agent.llms import LLM
from bee_agent.memory.summarize_memory import SummarizeMemory
from bee_agent.memory.message import BaseMessage, Role
import asyncio


async def main():
    try:
        # Initialize the LLM with parameters
        llm = LLM(model="llama3.2", parameters={"temperature": 0, "num_predict": 250})

        # Create summarize memory instance
        memory = SummarizeMemory(llm)

        # Add messages
        await memory.add_many(
            [
                BaseMessage.of(
                    {"role": Role.SYSTEM, "text": "You are a guide through France."}
                ),
                BaseMessage.of({"role": Role.USER, "text": "What is the capital?"}),
                BaseMessage.of({"role": Role.ASSISTANT, "text": "Paris"}),
                BaseMessage.of(
                    {"role": Role.USER, "text": "What language is spoken there?"}
                ),
            ]
        )

        # Print results
        print(f"Is Empty: {memory.is_empty()}")
        print(f"Message Count: {len(memory.messages)}")

        if memory.messages:
            print(f"Summary: {memory.messages[0].text}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback

        print(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(main())
