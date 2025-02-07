# SPDX-License-Identifier: Apache-2.0

import asyncio

from bee_agent.memory import UnconstrainedMemory
from bee_agent.memory.message import BaseMessage
from bee_agent.utils import Role


async def main():
    try:
        # Create memory instance
        memory = UnconstrainedMemory()

        # Add a message
        await memory.add(BaseMessage.of({"role": Role.USER, "text": "Hello world!"}))

        # Print results
        print(f"Is Empty: {memory.is_empty()}")  # Should print: False
        print(f"Message Count: {len(memory.messages)}")  # Should print: 1

        print("\nMessages:")
        for msg in memory.messages:
            print(f"{msg.role}: {msg.text}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback

        print(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(main())
