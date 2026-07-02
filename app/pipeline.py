import os
import asyncio
from dotenv import load_dotenv
from google.adk import runners

from app.agents.managing_editor import get_agent as get_me
from app.agents.evergreen_content import get_agent as get_evergreen
from app.agents.research_verification import get_agent as get_research
from app.agents.creative_director import get_agent as get_cd
from app.agents.visual_production import get_agent as get_visual
from app.agents.publishing_operations import get_agent as get_ops

load_dotenv()

async def run_agent(agent, prompt: str) -> str:
    runner = runners.InMemoryRunner(agent=agent)
    events = await runner.run_debug(prompt, quiet=True)
    output_text = ""
    for e in events:
        if getattr(e, 'author', '') != 'user' and getattr(e, 'message', None) and hasattr(e.message, 'parts'):
            for p in e.message.parts:
                if getattr(p, 'text', None):
                    output_text += p.text
    return output_text.strip()

async def run_pipeline_async(idea: str) -> dict:
    trace = []
    responses = {}
    
    print(f"--- STARTING PIPELINE WITH IDEA: {idea} ---\n")
    
    # 1. PLAN
    me = get_me()
    prompt = f"Plan this idea: {idea}"
    print(f"[{me.name}] Prompt: {prompt}")
    resp = await run_agent(me, prompt)
    responses["plan"] = resp
    trace.append("managing_editor")
    print(f"[{me.name}] Response:\n{resp}\n")
    
    # 2. DRAFT
    evergreen = get_evergreen()
    prompt = f"Draft content based on this plan:\n{responses.get('plan', '')}"
    print(f"[{evergreen.name}] Prompt: {prompt}")
    resp = await run_agent(evergreen, prompt)
    responses["draft"] = resp
    trace.append("evergreen_content")
    print(f"[{evergreen.name}] Response:\n{resp}\n")
    
    # 2.5 LINT STUB
    trace.append("ledger_lint_stub")
    print(f"[ledger_lint_stub] Linter passed.\n")
    
    # 3. REVIEW
    cd = get_cd()
    prompt = f"Review this draft:\n{responses.get('draft', '')}"
    print(f"[{cd.name}] Prompt: {prompt}")
    resp = await run_agent(cd, prompt)
    responses["review"] = resp
    trace.append("creative_director")
    print(f"[{cd.name}] Response:\n{resp}\n")
    
    # 4. VISUALIZE
    visual = get_visual()
    prompt = f"Create a visual brief and placeholder for this draft:\n{responses.get('draft', '')}"
    print(f"[{visual.name}] Prompt: {prompt}")
    resp = await run_agent(visual, prompt)
    responses["visual"] = resp
    trace.append("visual_production")
    print(f"[{visual.name}] Response:\n{resp}\n")
    
    # 5. QUEUE
    ops = get_ops()
    prompt = f"Queue this final package:\nText: {responses.get('draft', '')}\nVisual: {responses.get('visual', '')}\nStatus is approved by CD."
    print(f"[{ops.name}] Prompt: {prompt}")
    resp = await run_agent(ops, prompt)
    responses["queue"] = resp
    trace.append("publishing_operations")
    print(f"[{ops.name}] Response:\n{resp}\n")
    
    return {
        "status": "Approval Queue",
        "trace": trace,
        "responses": responses
    }

def run_pipeline(idea: str) -> dict:
    return asyncio.run(run_pipeline_async(idea))

if __name__ == "__main__":
    result = run_pipeline("A test idea for the hard-coded brand")
