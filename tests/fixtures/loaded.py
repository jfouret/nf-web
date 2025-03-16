import pytest
from .base import *

@pytest.fixture(scope="session")
def loaded_browser_context():
    """Create a logged-in browser context with page and server URL."""
    gpage = gen_page()
    gserver_url = gen_flask_server()
    page = next(gpage)
    server_url = next(gserver_url)
    login_action(page, server_url)
    
    pipelines = [
        {"organization": "nexomis", "project": "primary"},
        {"organization": "epi2me-labs", "project": "wf-basecalling"},
        {"organization": "nf-core", "project": "demo"}
    ]

    for pipeline in pipelines:
        page.goto(f"{server_url}/import_pipeline")
        page.fill("input#repoInput", f"{pipeline['organization']}/{pipeline['project']}")
        page.click("button[type='submit']")
        success_message = page.locator("#successMessage")
        success_message.wait_for(state = "visible", timeout=5000)
        assert success_message.inner_text() == "Pipeline imported successfully."
    
    page.goto(f"{server_url}/home")
    return page, server_url, pipelines
