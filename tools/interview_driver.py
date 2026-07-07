"""Drive the onboarding interview on camera: the owner's answers, typed live.

Runs onboard_brand.py in a pty, streams the Strategist's output to the
recording, and types each prepared owner answer character by character when
the CLI prompts. Falls back to safe confirmations if the interview asks more
questions than scripted; exits once the kit is ACTIVE.

Usage: .venv/bin/python tools/interview_driver.py demo/brand-packs/tapri-toast-club/
"""
import sys
import time
import pexpect

ANSWERS = [
    ("The draft looks right. One correction on locale: say 'near Sarafa, Indore' "
     "- neighbourhood only, never an exact address. Please continue."),
    ("Never any health, diet, digestion, energy, 'clean', 'natural' or "
     "'preservative-free' claims. Butter is butter - never call it healthy. "
     "No caffeine benefit claims. Never '100 percent' anything."),
    ("Never reveal the overnight dough method or timings, the masala-chai spice "
     "mix, our flour or butter suppliers' names, purchase prices, or the "
     "sand-timer brew timings. The phrases 'slow overnight dough' and 'flip the "
     "timer twice' are fine - the numbers behind them are not."),
    ("Chai content is never aimed at school kids - college-age and adults only. "
     "Never show grabbing toast straight off the tawa bare-handed. The judge on "
     "stool number four is brand lore, never a real person's likeness. Sarafa "
     "is our neighbourhood, not our address."),
    ("Good catch - refuse that one. Yes, add it as a standing rule."),
    ("Confirmed. Please compile, validate and save the Brand Kit now."),
]
FALLBACK = "Yes, confirmed - please proceed."
MAX_TURNS = 14


def type_line(child, text):
    for ch in text:
        child.send(ch)
        time.sleep(0.012)
    child.send("\r")


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "demo/brand-packs/tapri-toast-club/"
    child = pexpect.spawn(
        ".venv/bin/python", ["onboard_brand.py", src],
        encoding="utf-8", timeout=420, dimensions=(30, 100),
    )
    child.logfile_read = sys.stdout
    i = 0
    active = False
    while True:
        idx = child.expect([r"You: ", pexpect.EOF, pexpect.TIMEOUT])
        if idx != 0:
            break
        buf = child.before or ""
        if "now ACTIVE" in buf:
            active = True
        if active or i >= MAX_TURNS:
            time.sleep(1.0)
            type_line(child, "exit")
            child.expect(pexpect.EOF)
            break
        answer = ANSWERS[i] if i < len(ANSWERS) else FALLBACK
        # If the kit compiled early, don't keep answering — close out.
        time.sleep(1.2)
        type_line(child, answer)
        i += 1
    sys.exit(0)


if __name__ == "__main__":
    main()
