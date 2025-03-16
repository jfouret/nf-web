import pytest
import time
import pandas as pd
from io import StringIO

def test_import_pipeline_and_verify(loaded_browser_context):
    """Test importing a pipeline and verifying it appears in the pipelines list."""
    page, server_url, pipelines = loaded_browser_context
    
    # Navigate to import pipeline page
    page.goto(f"{server_url}/pipelines")
    
    table = page.locator("#app table")
    table.wait_for(timeout=5000)
    table_content = table.inner_html()
    generated_table = False
    # Wait for Vue.js to render the table
    while not generated_table:
        time.sleep(0.2)
        gtable = page.locator("#app table")
        gtable.wait_for(timeout=5000)
        gtable_content = table.inner_html()
        generated_table = gtable_content == table_content
        table_content = gtable_content
    df = pd.read_html(StringIO("<table>"+table_content+"</table>"))[0]
    
    for pipeline in pipelines:
        found_project = df.apply(lambda row: pipeline["organization"] == row.values[1] and pipeline["project"] == row.values[2], axis=1).any()
        assert found_project, f"No row found containing '{pipeline["organization"]}/{pipeline["project"]}'"
