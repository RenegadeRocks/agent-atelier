import os
from pathlib import Path
from google.adk import Agent
from app.agents.config import FLASH_MODEL

def get_agent():
    instruction = Path("specs/agents/visual-production.md").read_text(encoding="utf-8")
    return Agent(
        name="visual_production",
        model=FLASH_MODEL,
        instruction=instruction + "\n\nCRITICAL DIRECTIVE: You are running a test execution for Contract P1-A. Provide a text-free placeholder image reference and alt text."
    )
