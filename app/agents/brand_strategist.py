import os
from pathlib import Path
from google.adk import Agent
from app.agents.config import REASONING_MODEL

def get_agent():
    instruction = Path("specs/agents/brand-strategist.md").read_text(encoding="utf-8")
    
    # Also load the skill for context
    skill_content = Path("specs/skills/intake-interview/SKILL.md").read_text(encoding="utf-8")
    
    return Agent(
        name="brand_strategist",
        model=REASONING_MODEL,
        instruction=instruction + "\n\n=== INTAKE INTERVIEW SKILL ===\n" + skill_content
    )
