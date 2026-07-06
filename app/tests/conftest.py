import os
import pytest

def pytest_configure(config):
    config.addinivalue_line("markers", "live: mark test as requiring a live API key")

def pytest_collection_modifyitems(config, items):
    if os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY"):
        return
    skip_live = pytest.mark.skip(reason="need GOOGLE_API_KEY to run live tests")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)

@pytest.fixture(autouse=True)
def mock_semantic_review_judge(request, monkeypatch):
    if "live" not in request.keywords:
        async def mock_judge(agent, prompt, brand_kit):
            return "VERDICT: APPROVED (Stubbed for deterministic routing test)"
        import app.pipeline
        monkeypatch.setattr(app.pipeline, "semantic_review_judge", mock_judge)
