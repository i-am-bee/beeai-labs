import asyncio

from bee_agent.memory.sliding_memory import SlidingMemory, SlidingMemoryConfig
from bee_agent.memory.message import BaseMessage
from bee_agent.utils import Role


async def main():
    try:
        # Create sliding memory with size 3
        memory = SlidingMemory(
            SlidingMemoryConfig(
                size=3,
                handlers={
                    "removal_selector": lambda messages: messages[
                        0
                    ]  # Remove oldest message
                },
            )
        )

        # Add messages
        await memory.add(
            BaseMessage.of(
                {"role": Role.SYSTEM, "text": "You are a helpful assistant."}
            )
        )

        await memory.add(BaseMessage.of({"role": Role.USER, "text": "What is Python?"}))

        await memory.add(
            BaseMessage.of(
                {"role": Role.ASSISTANT, "text": "Python is a programming language."}
            )
        )

        # Adding a fourth message should trigger sliding window
        await memory.add(
            BaseMessage.of({"role": Role.USER, "text": "What about JavaScript?"})
        )

        # Print results
        print(f"Messages in memory: {len(memory.messages)}")  # Should print 3
        for msg in memory.messages:
            print(f"{msg.role}: {msg.text}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback

        print(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(main())
