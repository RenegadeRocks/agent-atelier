import yaml
from pathlib import Path
import re
import difflib

# Load policies.yaml
POLICY_PATH = Path(__file__).parent.parent / "specs" / "policies.yaml"
with open(POLICY_PATH) as f:
    POLICIES = yaml.safe_load(f)

def check_structural_gate(role: str, tool: str, environment: str = "preview") -> bool:
    """
    Evaluates the default-deny structural gate.
    """
    if environment not in POLICIES.get("environments", {}):
        return False
        
    blocked_in_env = POLICIES["environments"][environment].get("blocked_tools", [])
    if tool in blocked_in_env:
        return False
        
    roles = POLICIES.get("roles", {})
    if role not in roles:
        return False
        
    env_config = roles[role].get("environments", {}).get(environment, {})
    allowed_tools = env_config.get("allowed_tools", [])
    
    return tool in allowed_tools

def normalize_text(text: str) -> str:
    # NFKC, lowercase, strip punctuation except %, collapse whitespace
    text = text.lower()
    text = re.sub(r'[^\w\s%]', '', text)
    return ' '.join(text.split())

def extract_numbers(text: str) -> list[str]:
    # Extracts numbers, including decimals and percentages
    return sorted(re.findall(r'\d+(?:\.\d+)?%?', text))

def calculate_token_set_ratio(s1: str, s2: str) -> int:
    # Simple token set ratio approximation (difflib based)
    tokens1 = set(s1.split())
    tokens2 = set(s2.split())
    intersection = tokens1.intersection(tokens2)
    if not tokens1 and not tokens2:
        return 100
    if not tokens1 or not tokens2:
        return 0
    return int(len(intersection) / max(len(tokens1), len(tokens2)) * 100)

def content_gauntlet(piece_id: str, caption: str, brand_kit: dict, claim_bank: list[dict] = None) -> dict:
    """
    The deterministic content gauntlet.
    Runs fail-closed safety, deterministic rule scanning, and claim grounding.
    """
    if claim_bank is None:
        claim_bank = []
        
    # 1. Fail-closed safety
    for field in ["claims_forbidden", "non_disclosure_rules", "required_framing"]:
        val = brand_kit.get(field, [])
        # If it's a string, treat as single item list; if None or empty list, it's empty
        if not val or (isinstance(val, list) and len(val) == 0):
            return {"status": "BLOCK", "reason": f"Fail-closed: safety field '{field}' is empty or unconfirmed."}
            
    # 2. Deterministic rule scan
    # We scan for exact phrase hits to satisfy the deterministic gauntlet rider without LLM
    rules_to_scan = {
        "claims_forbidden": brand_kit.get("claims_forbidden", []),
        "non_disclosure_rules": brand_kit.get("non_disclosure_rules", []),
        "cta_forbidden_phrases": brand_kit.get("cta_forbidden_phrases", [])
    }
    
    caption_lower = caption.lower()
    for rule_name, phrases in rules_to_scan.items():
        if isinstance(phrases, str):
            phrases = [phrases]
        for phrase in phrases:
            # Deterministic scan: if the phrase verbatim exists in the caption (or a simplified check)
            # In a real system without LLM, this checks for direct substring matches of the rule values.
            if phrase.lower() in caption_lower:
                return {"status": "BLOCK", "reason": f"Safety violation ({rule_name}): {phrase}"}

    # Comparative claims flag
    comparative_allowed = brand_kit.get("comparative_claims_allowed", False)
    if str(comparative_allowed).lower() == "false":
        # Deterministic check for comparative markers as a proxy
        comparative_markers = ["better than", "more than", "faster than", "superior", "beats", "competitor"]
        for marker in comparative_markers:
            if marker in caption_lower:
                return {"status": "BLOCK", "reason": f"Safety violation (comparative_claims_allowed=false): {marker}"}
                
    # 3. Claim Grounding
    # Find sentences in caption
    sentences = re.split(r'(?<=[.!?]) +', caption)
    lexicon = POLICIES["deterministic_checks"][0]["claim_trigger_lexicon"]["terms"]
    
    verified_claims = [c for c in claim_bank if c.get("status") == "VERIFIED"]
    
    for sentence in sentences:
        nums = extract_numbers(sentence)
        has_num = len(nums) > 0
        has_percentage = any('%' in n for n in nums)
        has_lexicon = any(term in sentence.lower() for term in lexicon)
        
        if (has_num and has_lexicon) or has_percentage:
            # Triggered! Must find a near-verbatim match in verified_claims
            if not verified_claims:
                return {"status": "BLOCK", "reason": f"Claim grounding violation: unverified quantitative claim '{sentence}' (thin research bank)."}
                
            matched = False
            for claim in verified_claims:
                locked = claim.get("locked_sentence", "")
                locked_nums = extract_numbers(locked)
                
                # Numeric equality
                if nums == locked_nums:
                    # Near-verbatim text match
                    score = calculate_token_set_ratio(normalize_text(sentence), normalize_text(locked))
                    threshold = POLICIES["deterministic_checks"][0]["requires"]["match_threshold"]
                    if score >= threshold:
                        matched = True
                        break
                        
            if not matched:
                return {"status": "BLOCK", "reason": f"Claim grounding violation: unverified quantitative claim '{sentence}'."}
                
    return {"status": "PASS"}

# Exposed re-gate function for human-edited content (P5-A socket)
def re_gate_human_edit(piece_id: str, new_caption: str, brand_kit: dict, claim_bank: list[dict] = None) -> dict:
    return content_gauntlet(piece_id, new_caption, brand_kit, claim_bank)
