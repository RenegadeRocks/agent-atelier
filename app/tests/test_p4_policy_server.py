import pytest
from app.policy_server import check_structural_gate, content_gauntlet

def test_structural_gate_default_deny():
    # Roles defined in policies.yaml
    assert check_structural_gate("evergreen_content_agent", "draft_doc", "preview") == True
    assert check_structural_gate("evergreen_content_agent", "instagram_publish", "production") == False
    assert check_structural_gate("publishing_agent", "instagram_publish", "production") == True
    # Default-deny for undefined roles
    assert check_structural_gate("hacker_agent", "read_ledger", "preview") == False

def test_structural_gate_preview_blocked():
    # Publishing agent can publish in production but NOT in preview
    assert check_structural_gate("publishing_agent", "instagram_publish", "preview") == False
    assert check_structural_gate("publishing_agent", "instagram_publish", "production") == True

def test_fail_closed_safety_empty_field():
    brand_kit_empty = {
        "claims_forbidden": [],
        "non_disclosure_rules": ["do not reveal the secret"],
        "required_framing": ["always be nice"]
    }
    # Empty claims_forbidden
    res = content_gauntlet("piece1", "A simple caption.", brand_kit_empty)
    assert res["status"] == "BLOCK"
    assert "empty or unconfirmed" in res["reason"]

def test_deterministic_gauntlet_claims_forbidden_hit():
    brand_kit = {
        "claims_forbidden": ["guarantees success"],
        "non_disclosure_rules": ["secret project"],
        "required_framing": ["positive"]
    }
    caption = "This new formula guarantees success instantly!"
    res = content_gauntlet("piece1", caption, brand_kit)
    assert res["status"] == "BLOCK"
    assert "claims_forbidden" in res["reason"]
    assert "guarantees success" in res["reason"]

def test_deterministic_gauntlet_non_disclosure_leak():
    brand_kit = {
        "claims_forbidden": ["fake"],
        "non_disclosure_rules": ["Project Titan"],
        "required_framing": ["positive"]
    }
    caption = "Here is a sneak peek at Project Titan."
    res = content_gauntlet("piece1", caption, brand_kit)
    assert res["status"] == "BLOCK"
    assert "non_disclosure_rules" in res["reason"]
    assert "Project Titan" in res["reason"]

def test_deterministic_gauntlet_cta_forbidden_phrase():
    brand_kit = {
        "claims_forbidden": ["fake"],
        "non_disclosure_rules": ["secret"],
        "required_framing": ["positive"],
        "cta_forbidden_phrases": ["click the link in bio"]
    }
    caption = "Check it out, click the link in bio!"
    res = content_gauntlet("piece1", caption, brand_kit)
    assert res["status"] == "BLOCK"
    assert "cta_forbidden_phrases" in res["reason"]

def test_deterministic_gauntlet_comparative_claim():
    brand_kit = {
        "claims_forbidden": ["fake"],
        "non_disclosure_rules": ["secret"],
        "required_framing": ["positive"],
        "comparative_claims_allowed": False
    }
    caption = "Our coffee is better than the rest."
    res = content_gauntlet("piece1", caption, brand_kit)
    assert res["status"] == "BLOCK"
    assert "comparative_claims_allowed" in res["reason"]

def test_claim_grounding_unverified_thin_bank():
    brand_kit = {
        "claims_forbidden": ["fake"],
        "non_disclosure_rules": ["secret"],
        "required_framing": ["positive"]
    }
    caption = "Research shows that 99% of people agree."
    # Thin research bank (empty) blocks instead of passing
    res = content_gauntlet("piece1", caption, brand_kit, claim_bank=[])
    assert res["status"] == "BLOCK"
    assert "thin research bank" in res["reason"]

def test_claim_grounding_unverified_claim():
    brand_kit = {
        "claims_forbidden": ["fake"],
        "non_disclosure_rules": ["secret"],
        "required_framing": ["positive"]
    }
    caption = "Research shows that 99% of people agree."
    claim_bank = [{"status": "VERIFIED", "locked_sentence": "Research shows that 50% of people agree."}]
    res = content_gauntlet("piece1", caption, brand_kit, claim_bank)
    assert res["status"] == "BLOCK"
    assert "unverified quantitative claim" in res["reason"]

def test_claim_grounding_verified_claim():
    brand_kit = {
        "claims_forbidden": ["fake"],
        "non_disclosure_rules": ["secret"],
        "required_framing": ["positive"]
    }
    # Matches exactly 99% and has high token match to the locked_sentence
    caption = "Research shows that 99% of users agree."
    claim_bank = [{"status": "VERIFIED", "locked_sentence": "Research shows that 99% of users agree."}]
    res = content_gauntlet("piece1", caption, brand_kit, claim_bank)
    assert res["status"] == "PASS"
