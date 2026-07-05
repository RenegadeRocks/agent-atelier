import re
import json

def test_json_extraction():
    # Mocked agent reply containing normal prose and a JSON block at the end
    draft_reply = """Here is the draft content based on the plan.

I have followed all instructions and crafted a compelling narrative for the brand.

```json
{
    "idea_sentence": "This is a great idea.",
    "caption": "This is a captivating caption with a specific detail: the 4:05 PM sink dump.",
    "hook_text": "STOP THE SINK DUMP",
    "visual_brief": "MESSAGE: The daily toll of operational chaos on a founder's time."
}
```"""

    blocks = re.findall(r'```json\s*(.*?)\s*```', draft_reply, re.DOTALL)
    assert len(blocks) == 1
    
    draft_data = json.loads(blocks[-1])
    assert draft_data["idea_sentence"] == "This is a great idea."
    assert draft_data["caption"] == "This is a captivating caption with a specific detail: the 4:05 PM sink dump."
    assert draft_data["hook_text"] == "STOP THE SINK DUMP"
    assert draft_data["visual_brief"] == "MESSAGE: The daily toll of operational chaos on a founder's time."

def test_json_extraction_alt_text():
    alt_reply = """Here is the alt text you requested.

```json
{
    "alt_text": "A cinematic, close-up photograph capturing a moment of operational fatigue."
}
```"""
    blocks = re.findall(r'```json\s*(.*?)\s*```', alt_reply, re.DOTALL)
    assert len(blocks) == 1
    
    alt_data = json.loads(blocks[-1])
    assert alt_data["alt_text"] == "A cinematic, close-up photograph capturing a moment of operational fatigue."
