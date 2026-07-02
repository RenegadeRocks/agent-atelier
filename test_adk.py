import os
import asyncio
from dotenv import load_dotenv
from google.adk import Agent, runners

load_dotenv()

async def main():
    agent = Agent(name="test_agent", model="gemini-3.0-pro", instruction="Say 'hello'")
    # Let's try InMemoryRunner
    runner = runners.InMemoryRunner(agent=agent)
    events = await runner.run_debug("Hi")
    for event in events:
        if getattr(event, 'output', None):
            print("Response:", event.output.message.content)

if __name__ == "__main__":
    asyncio.run(main())
