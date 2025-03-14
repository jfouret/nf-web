import os
import pytest
import tempfile
import threading
import time
import subprocess
import socket
from pathlib import Path

def ensure_firefox_installed():
    """Ensure Firefox browser is installed for Playwright."""
    print("Ensuring Firefox browser is installed for Playwright...")
    # The install command is idempotent - safe to run multiple times
    subprocess.run(["python", "-m", "playwright", "install", "firefox"], check=True)

# Ensure Firefox is installed before running tests
ensure_firefox_installed()

@pytest.fixture(scope="session")
def app_with_test_config():
    """Create a Flask app with test configuration."""
    # Create a temporary directory for test data
    test_dir = tempfile.mkdtemp()

    envs = {
        "LITEFLOW_ROOT_DIR": test_dir,
        "LITEFLOW_LOGIN_PASSWORD": "testpassword123",
        "LITEFLOW_SECRET_KEY": "test_secret_key"
    }

    for key, value in envs.items():
        os.environ[key] = value
    
    # Create the app
    from liteflow import create_app
    flask_app = create_app()
    
    # Return the app
    yield flask_app
    
    # Clean up
    for key in envs.keys():
        os.environ.pop(key, None)

@pytest.fixture(scope="session")
def flask_server(app_with_test_config):
    """Start a Flask server for testing on a specific port."""
    
    for port in range(5000, 6000):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                break
        except OSError:
            continue

    def run_server():
        app_with_test_config.run(port = port)
    
    # Start server in a separate thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for server to start
    time.sleep(1)

    # Return the server URL
    yield f"http://127.0.0.1:{port}"
    
    # No explicit cleanup needed as thread is daemonic

@pytest.fixture(scope="session")
def playwright_browser():
    """Create a Playwright browser for testing."""
    from playwright.sync_api import sync_playwright
    
    playwright = sync_playwright().start()
    browser = playwright.firefox.launch(headless=True)
    
    yield browser
    
    browser.close()
    playwright.stop()

@pytest.fixture
def browser_context(playwright_browser, app_with_test_config):
    """Create a browser context with page and server URL for each test."""
    # Find an available port
    for port in range(5000, 6000):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                break
        except OSError:
            continue
    
    # Start server in a separate thread for this test only
    def run_server():
        app_with_test_config.run(port=port)
    
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for server to start
    time.sleep(1)
    
    # Create a new browser context and page
    context = playwright_browser.new_context()
    page = context.new_page()
    page.set_default_timeout(1000)
    
    # Create the server URL
    server_url = f"http://127.0.0.1:{port}"
    
    # Yield the tuple of (page, server_url)
    yield (page, server_url)
    
    # Clean up
    context.close()
    # Server thread will terminate automatically as it's a daemon thread

@pytest.fixture
def logged_in_browser_context(browser_context):
    """Create a logged-in browser context with page and server URL."""
    page, server_url = browser_context
    
    # Navigate to login page
    page.goto(f"{server_url}/login")
    
    # Get the master password from the app
    test_password = os.getenv("LITEFLOW_LOGIN_PASSWORD")
    
    # Fill in the password field
    page.fill("#password", test_password)
    
    # Increase timeout for this action
    page.set_default_timeout(5000)
    
    # Click the submit button and wait for navigation to complete
    with page.expect_navigation(url=f"{server_url}/home", wait_until="networkidle"):
        page.click("button.btn-primary")
    
    # Verify we're on the home page
    assert page.url == f"{server_url}/home", f"Failed to navigate to home page. Current URL: {page.url}"
    
    # Return the tuple with logged-in page
    return (page, server_url)

