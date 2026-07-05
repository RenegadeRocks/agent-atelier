import pytest
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

from app.brand_kit import load_brand_kit
from app.resolver import resolve, ResolveScope, MODEL, AUTH, SecretsVault, ResolveBlocked
from app.pipeline import run_pipeline

def test_missing_required_variable_blocks():
    """Missing required variable blocks the run (surfaces to owner)."""
    # Create a brand kit that is missing a required variable by overriding standard parsing
    # Or just use an empty dict for resolution where a required token is present
    
    brand_kit = {} # Empty
    template = "This needs [[BRAND_NAME]] which is required."
    env = {}
    vault = SecretsVault({})
    
    with pytest.raises(ResolveBlocked) as exc_info:
        resolve(template, brand_kit, env, vault, ResolveScope(MODEL))
    
    assert "ERR_REQUIRED_UNRESOLVED" in str(exc_info.value)
    assert "BRAND_NAME" in str(exc_info.value)

def test_secrets_never_inlined_in_model_scope():
    """Secrets are never inlined into model-visible text."""
    brand_kit = {"image_provider": "gemini_image_pro"}
    template = "Prompt text with [[SECRET:IMAGE_PROVIDER_KEY]]"
    env = {}
    vault = SecretsVault({"gemini_image_pro_api_key": "REAL_SECRET_VALUE"})
    
    with pytest.raises(ResolveBlocked) as exc_info:
        resolve(template, brand_kit, env, vault, ResolveScope(MODEL))
        
    assert "ERR_SECRET_IN_MODEL_CONTEXT" in str(exc_info.value)
    assert "REAL_SECRET_VALUE" not in str(exc_info.value)

def test_auth_scope_handles_secrets_correctly():
    """Auth scope correctly extracts secrets without inlining them in output."""
    brand_kit = {"image_provider": "gemini_image_pro"}
    template = "Auth text with [[SECRET:IMAGE_PROVIDER_KEY]]"
    env = {}
    vault = SecretsVault({"gemini_image_pro_api_key": "REAL_SECRET_VALUE"})
    
    scope = ResolveScope(AUTH)
    out = resolve(template, brand_kit, env, vault, scope)
    
    # Secret shouldn't be in the resolved text
    assert "REAL_SECRET_VALUE" not in out
    assert "SECRET" not in out
    
    # But it should be in the scope's auth_secrets
    assert scope.auth_secrets.get("SECRET:IMAGE_PROVIDER_KEY") == "REAL_SECRET_VALUE"

def test_aol_appendix_a_validates():
    """The AOL Appendix-A kit validates successfully against the JSON schema."""
    kit = load_brand_kit('brands/aol/brand_kit.yaml', 'specs/brand_kit.schema.json')
    assert kit['brand_name'] == "Art of Living Ludhiana"
    assert kit['claims_forbidden_confirmed'] is True

@pytest.mark.live
def test_pipeline_processes_aol_brand():
    """The pipeline successfully processes the AOL brand via brand_kit.yaml."""
    # Deterministic test
    result = run_pipeline("A test idea for AOL", 'brands/aol/brand_kit.yaml')
    assert result["status"] == "Approval Queue"

@pytest.mark.live
def test_pipeline_processes_kanva_brand():
    """The pipeline successfully processes the kanva brand via its brand_kit.yaml with zero code changes."""
    # Deterministic test
    result = run_pipeline("A test idea for Kanva", 'brands/kanva-coffee/brand_kit.yaml')
    assert result["status"] == "Approval Queue"

from unittest.mock import patch
from app.tools.caption_compose_server import caption_compose_handle_call_tool

@patch("PIL.ImageDraw.ImageDraw.rectangle")
@patch("PIL.ImageDraw.ImageDraw.text")
def test_compositor_uses_brand_kit(mock_text, mock_rect, tmp_path):
    # Create a dummy image
    from PIL import Image
    dummy_img = tmp_path / "gen_dummy.jpg"
    Image.new("RGB", (1080, 1080), (255, 255, 255)).save(dummy_img, "JPEG")
    
    # Test AOL
    aol_kit = load_brand_kit('brands/aol/brand_kit.yaml', 'specs/brand_kit.schema.json')
    caption_compose_handle_call_tool("caption_compose", {
        "image_url": str(dummy_img),
        "caption": "Test AOL",
        "brand_kit": aol_kit
    })
    
    # Assert AOL Wordmark
    expected_aol_wordmark = " ".join(list(aol_kit.get('wordmark_text', '').upper()))
    assert any(expected_aol_wordmark in str(call) for call in mock_text.call_args_list), f"AOL Wordmark '{expected_aol_wordmark}' missing"
    
    # Assert AOL Accent (AOL light theme accent)
    aol_accent = aol_kit.get('accent_light_bg', '').lower()
    assert any(f"fill='{aol_accent}'" in str(call).lower() for call in mock_rect.call_args_list), f"AOL Accent '{aol_accent}' missing"
    
    mock_text.reset_mock()
    mock_rect.reset_mock()
    
    # Test Kanva
    kanva_kit = load_brand_kit('brands/kanva-coffee/brand_kit.yaml', 'specs/brand_kit.schema.json')
    caption_compose_handle_call_tool("caption_compose", {
        "image_url": str(dummy_img),
        "caption": "Test Kanva",
        "brand_kit": kanva_kit
    })
    
    # Assert Kanva Wordmark
    expected_kanva_wordmark = " ".join(list(kanva_kit.get('wordmark_text', '').upper()))
    assert any(expected_kanva_wordmark in str(call) for call in mock_text.call_args_list), f"Kanva Wordmark '{expected_kanva_wordmark}' missing"
    
    # Assert Kanva Accent (Kanva light theme accent)
    kanva_accent = kanva_kit.get('accent_light_bg', '').lower()
    assert any(f"fill='{kanva_accent}'" in str(call).lower() for call in mock_rect.call_args_list), f"Kanva Accent '{kanva_accent}' missing"

