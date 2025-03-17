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
    
    configs = [
        {
            "name": "Default Config",
            "filename": "default_config.config",
            "content": """
process:
  executor: local
  cpus: 2
  memory: 4GB
"""
        },
        {
            "name": "High Performance",
            "filename": "high_perf.config",
            "content": """
process:
  executor: slurm
  cpus: 16
  memory: 32GB
"""
        },
        {
            "name": "Low Resource",
            "filename": "low_resource.config",
            "content": """
process:
  executor: local
  cpus: 2
  memory: 4GB
"""
        }
    ]

    # Add configs
    page.goto(f"{server_url}/configs")
    for i, config in enumerate(configs):
        page.fill("#inlineFormInputName", config["name"])
        page.fill("#inlineFormInputFileName", config["filename"])
        page.click("#createConfigBtn")
        
        page.wait_for_url(f"{server_url}/configs/edit/{config['filename']}")
        page.fill("#configContent", config["content"])
        page.click("#saveConfigBtn")
        
        page.wait_for_url(f"{server_url}/configs")
        
    # Set first config as default
    set_default_button = page.locator(f".set-default-btn[data-filename='{configs[0]['filename']}']")
    set_default_button.click()
    alert = page.locator(".alert.alert-success.alert-dismissible.fade.show")
    alert.wait_for()
    assert "Default configuration updated" in alert.inner_text()
    
    page.goto(f"{server_url}/home")
    return page, server_url, pipelines, configs
