import pytest
import time
import pandas as pd
from io import StringIO

def test_configs(loaded_browser_context):
    """Test that configs are correctly displayed in the configs page."""
    page, server_url, _, configs = loaded_browser_context
    
    page.goto(f"{server_url}/configs")
    table = page.locator("table")
    table.wait_for(timeout=5000)
    table_content = table.inner_html()
    df = pd.read_html(StringIO("<table>"+table_content+"</table>"))[0]
    
    for config in configs:
        found_config = df.apply(
            lambda row: config["name"] in row.values and config["filename"] in row.values, 
            axis=1
        ).any()
        assert found_config, f"Config '{config['name']}' with filename '{config['filename']}' not found in the table"
    
    visible_default_badges = page.locator("span.default-badge:visible")
    assert visible_default_badges.count() == 1, f"Expected exactly one visible default badge, found {visible_default_badges.count()}"
    default_filename = visible_default_badges.locator("xpath=..").get_attribute("data-filename")
    assert default_filename == configs[0]["filename"], f"Expected default badge to be on config with filename '{configs[0]['filename']}', found '{default_filename}'"
