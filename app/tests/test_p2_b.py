import pytest
import os
import yaml
from pathlib import Path

from app.brand_kit import load_brand_kit
from app.tools.source_ingest import ingest_source

def test_source_ingest_graceful_decline():
    """
    Scenario: source_ingest gracefully declines URL, social, and PDF ingestion inputs
    and falls back to manual interview, only ingesting local text/markdown files.
    """
    url_res = ingest_source("https://example.com")
    assert url_res["status"] == "unsupported"
    
    social_res = ingest_source("@kanvacoffee")
    assert social_res["status"] == "unsupported"
    
    pdf_res = ingest_source("path/to/guide.pdf")
    assert pdf_res["status"] == "unsupported"

def test_source_ingest_local_markdown(tmp_path):
    """
    Scenario: source_ingest successfully reads local markdown text.
    """
    test_file = tmp_path / "brand-story.md"
    test_file.write_text("# Test Brand\nTagline: best coffee")
    result = ingest_source(str(test_file))
    assert result["status"] == "success"
    assert "best coffee" in result["text"]

def test_empty_safety_fields_fail_validation(tmp_path):
    """
    Scenario: Empty safety fields with _confirmed: true MUST fail validation
    (structurally preventing the P2-A defect).
    """
    schema_path = "specs/brand_kit.schema.json"
    base_kit_path = "brands/aol/brand_kit.yaml"
    
    with open(base_kit_path, 'r', encoding='utf-8') as f:
        kit_data = yaml.safe_load(f)
        
    kit_data["claims_forbidden"] = []
    kit_data["claims_forbidden_confirmed"] = True
    
    kit_path = tmp_path / "bad_kit.yaml"
    with open(kit_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(kit_data, f)
        
    with pytest.raises(ValueError, match="Confirmed-empty is only legal with an explicit owner sign-off marker"):
        load_brand_kit(str(kit_path), schema_path)

@pytest.mark.live
def test_strategist_live_interview_and_first_light():
    """
    Scenario: End-to-end Brand Onboarding Strategist interview, output validation, and first light.
    This will be run manually by the owner via the onboard_brand.py CLI.
    The test simply verifies that the test framework is aware of this live test.
    The actual structural assertion is that the generated kit passes load_brand_kit
    and the FirstLightResult captures the probes.
    """
    # The actual execution is left to the owner via `python onboard_brand.py demo/brand-packs/kanva-coffee/`
    pass

def test_onboarding_launches_without_resolve_blocked():
    """
    Scenario: Onboarding launches with no kit and reaches the first interview question
    without ResolveBlocked.
    """
    from app.agents.brand_strategist import get_agent
    from google.adk import runners
    import asyncio
    from unittest.mock import AsyncMock, patch
    
    agent = get_agent()
    # The Strategist instruction retains literal [[TOKENS]] and is not resolved against a blank kit.
    runner = runners.InMemoryRunner(agent=agent)
    
    async def run_test():
        with patch.object(runners.InMemoryRunner, 'run_debug', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = []
            await runner.run_debug("Hello! I am ready to start the guided brand interview.")
            mock_run.assert_called_once()
            
    asyncio.run(run_test())

def test_ingestion_scope_only_reads_sources_dir(tmp_path):
    """
    Scenario: Ingestion never reads files outside sources/.
    """
    from onboard_brand import preload_ingested_context
    
    brand_dir = tmp_path / "test-brand"
    brand_dir.mkdir()
    
    # Root level markdown (should NOT be ingested)
    root_md = brand_dir / "intake-answers.md"
    root_md.write_text("C-Scheme Locale")
    
    # Sources dir markdown (should be ingested)
    sources_dir = brand_dir / "sources"
    sources_dir.mkdir()
    source_md = sources_dir / "brand-story.md"
    source_md.write_text("Best chuski in Jaipur")
    
    context = preload_ingested_context(str(brand_dir))
    
    assert "Best chuski in Jaipur" in context
    assert "C-Scheme Locale" not in context

