import pytest
import os
import shutil
from app.approval_protocol import process_approval_action
from app.instagram_adapter import instagram_publish
from app.post_kit import export_post_kit

# Mock data
brand_kit = {
    "claims_forbidden": ["guaranteed"],
    "non_disclosure_rules": ["secret ingredient"],
    "required_framing": ["positive"],
    "research_post_min_per_week": 0
}

claim_bank = []

def test_poller_actions_approve():
    # Simulate an Approve action on a clean caption
    caption = "This is a simple caption with no numbers."
    result = process_approval_action(
        piece_id="TEST-1",
        status="Approval Queue",
        owner_action="Approve",
        caption=caption,
        brand_kit=brand_kit,
        claim_bank=claim_bank,
        ledger_rows=[]
    )
    assert result["ok"] is True
    assert result["new_status"] == "Approved"

def test_poller_actions_request_changes():
    result = process_approval_action(
        piece_id="TEST-1",
        status="Approval Queue",
        owner_action="Request changes",
        caption="Any caption",
        brand_kit=brand_kit,
        claim_bank=claim_bank,
        ledger_rows=[]
    )
    assert result["ok"] is True
    assert result["new_status"] == "CD Review"
    assert result["detail"] == "Owner requested changes"

def test_poller_actions_reject():
    result = process_approval_action(
        piece_id="TEST-1",
        status="Approval Queue",
        owner_action="Reject",
        caption="Any caption",
        brand_kit=brand_kit,
        claim_bank=claim_bank,
        ledger_rows=[]
    )
    assert result["ok"] is True
    assert result["new_status"] == "Archived"

def test_poller_actions_mark_posted():
    result = process_approval_action(
        piece_id="TEST-1",
        status="Approved",
        owner_action="Mark posted",
        caption="Any caption",
        brand_kit=brand_kit,
        claim_bank=claim_bank,
        ledger_rows=[]
    )
    assert result["ok"] is True
    assert result["new_status"] == "Published"

def test_re_gate_on_every_approve():
    # If the caption contains a number but no claim bank entry, policy_server should block it
    caption_with_claim = "This improves productivity by 50%."
    result = process_approval_action(
        piece_id="TEST-2",
        status="Approval Queue",
        owner_action="Approve",
        caption=caption_with_claim,
        brand_kit=brand_kit,
        claim_bank=claim_bank,  # empty claim bank
        ledger_rows=[]
    )
    assert result["ok"] is False
    assert "refused_regate" in result["error"]
    assert result["new_status"] == "Approval Queue"
    
    # Test deterministic scan block (claims_forbidden)
    caption_forbidden = "This is guaranteed to work."
    result2 = process_approval_action(
        piece_id="TEST-3",
        status="Approval Queue",
        owner_action="Approve",
        caption=caption_forbidden,
        brand_kit=brand_kit,
        claim_bank=claim_bank,
        ledger_rows=[]
    )
    assert result2["ok"] is False
    assert "refused_regate" in result2["error"]
    assert "guaranteed" in result2["error"]

def test_adapterless_surfacing():
    with pytest.raises(NotImplementedError) as exc_info:
        instagram_publish(
            piece_id="TEST-4",
            image_urls=["http://example.com/image.jpg"],
            caption="Test"
        )
    assert "won't auto-publish — hand off by hand" in str(exc_info.value)

def test_first_committed_wins_stale_action():
    # If the piece is already Published, a new action from another operator should fail/be ignored
    result = process_approval_action(
        piece_id="TEST-5",
        status="Published",
        owner_action="Reject",
        caption="Test",
        brand_kit=brand_kit,
        claim_bank=claim_bank,
        ledger_rows=[]
    )
    assert result["ok"] is False
    assert result["new_status"] == "Published"

def test_post_kit_export(tmpdir):
    # Change cwd to tmpdir for testing
    import os
    original_cwd = os.getcwd()
    os.chdir(str(tmpdir))
    
    try:
        fake_jpeg = b"\xff\xd8\xff\xe0" + b"\x00" * 32  # valid JPEG magic
        handoff_dir = export_post_kit(
            piece_id="TEST-6",
            brand_id="test_brand",
            caption="Test Caption",
            asset_urls=["http://example.com/1.jpg", "http://example.com/2.jpg"],
            alt_texts=["Alt 1", "Alt 2"],
            fetch=lambda url: fake_jpeg,
        )

        assert os.path.exists(handoff_dir)
        assert os.path.exists(os.path.join(handoff_dir, "01.jpg"))
        assert os.path.exists(os.path.join(handoff_dir, "02.jpg"))
        with open(os.path.join(handoff_dir, "01.jpg"), "rb") as f:
            assert f.read().startswith(b"\xff\xd8\xff")  # real image bytes, never a placeholder
        assert not os.path.exists(os.path.join(handoff_dir, "KIT_INCOMPLETE.txt"))
        assert os.path.exists(os.path.join(handoff_dir, "caption.txt"))
        assert os.path.exists(os.path.join(handoff_dir, "alt_texts.txt"))
        assert os.path.exists(os.path.join(handoff_dir, "checklist.txt"))

        # Non-image download must fail LOUDLY — no fake slide, an error file + marker.
        bad_dir = export_post_kit(
            piece_id="TEST-7",
            brand_id="test_brand",
            caption="c",
            asset_urls=["http://example.com/broken.jpg"],
            alt_texts=["a"],
            fetch=lambda url: b"<html>404 not found</html>",
        )
        assert not os.path.exists(os.path.join(bad_dir, "01.jpg"))
        assert os.path.exists(os.path.join(bad_dir, "download_error_01.txt"))
        assert os.path.exists(os.path.join(bad_dir, "KIT_INCOMPLETE.txt"))
        
        with open(os.path.join(handoff_dir, "caption.txt"), "r") as f:
            assert f.read() == "Test Caption"
            
    finally:
        os.chdir(original_cwd)
