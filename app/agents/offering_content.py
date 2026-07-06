import os
from google.adk import agents
from app.agents.config import REASONING_MODEL

def get_agent() -> agents.Agent:
    """Returns the Offering Content Agent instance."""
    
    # Load the instruction from the pre-seeded spec
    instruction_path = os.path.join(
        os.path.dirname(__file__), 
        "../../specs/agents/offering-content.md"
    )
    
    try:
        with open(instruction_path, "r", encoding="utf-8") as f:
            instruction = f.read()
    except FileNotFoundError:
        # Fallback if somehow missing during test runs
        instruction = "You are the Offering Content Agent."
        
    return agents.Agent(
        name="Offering Content Agent",
        model=REASONING_MODEL,
        instruction=instruction,
        tools=[]
    )
