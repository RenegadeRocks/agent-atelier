import os
from pathlib import Path
from google.adk import Agent
from app.agents.config import REASONING_MODEL

def get_agent():
    instruction = Path("specs/agents/evergreen-content.md").read_text(encoding="utf-8")
    return Agent(
        name="evergreen_content",
        model=REASONING_MODEL,
        instruction=instruction + "\n\nCRITICAL DIRECTIVE: You are running a test execution for Contract P1-A. Create a short draft and visual brief for the given test idea."
    )
