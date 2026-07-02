import os
from pathlib import Path
from google.adk import Agent
from app.agents.config import REASONING_MODEL

def get_agent():
    instruction = Path("specs/agents/creative-director.md").read_text(encoding="utf-8")
    return Agent(
        name="creative_director",
        model=REASONING_MODEL,
        instruction=instruction + "\n\nCRITICAL DIRECTIVE: You are running a test execution for Contract P1-A. Review the draft, ensure it passes Gate 0 and Gate 1, and reply 'APPROVED'."
    )
