import os
from pathlib import Path
from google.adk import Agent
from app.agents.config import REASONING_MODEL

def get_agent():
    instruction = Path("specs/agents/managing-editor.md").read_text(encoding="utf-8")
    return Agent(
        name="managing_editor",
        model=REASONING_MODEL,
        instruction=instruction + "\n\nCRITICAL DIRECTIVE: You are running a test execution for Contract P1-A. When you receive a test idea, plan it out and assign it to evergreen_content, then explicitly return the result."
    )
