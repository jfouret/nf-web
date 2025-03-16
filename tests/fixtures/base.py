import os
import pytest
import tempfile
import threading
import time
import socket
from playwright.sync_api import sync_playwright

playwright = sync_playwright().start()

def gen_flask_server():
    """Start a Flask server for testing on a specific port."""

    test_dir = tempfile.mkdtemp()

    envs = {
        "LITEFLOW_ROOT_DIR": test_dir,
        "LITEFLOW_LOGIN_PASSWORD": "testpassword123",
        "LITEFLOW_SECRET_KEY": "test_secret_key"
    }

    for key, value in envs.items():
        os.environ[key] = value
    
    from liteflow import create_app
    flask_app = create_app()
    
    for port in range(5000, 6000):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                break
        except OSError:
            continue

    def run_server():
        flask_app.run(port = port)
    
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    time.sleep(1)
    yield f"http://127.0.0.1:{port}"
    for key in envs.keys():
        os.environ.pop(key, None)

def gen_page():
    """Create a Playwright browser for testing."""
    
    browser = playwright.firefox.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()
    browser.close()

@pytest.fixture(scope="session")
def browser_context():
    gpage = gen_page()
    gserver_url = gen_flask_server()
    page = next(gpage)
    server_url = next(gserver_url)
    yield (page, server_url)
    gpage.close()
    gserver_url.close()

def login_action(page, server_url):
    page.goto(f"{server_url}/login")
    test_password = os.getenv("LITEFLOW_LOGIN_PASSWORD")
    page.fill("#password", test_password)
    page.set_default_timeout(5000)
    with page.expect_navigation(url=f"{server_url}/home", wait_until="networkidle"):
        page.click("button.btn-primary")
    assert page.url == f"{server_url}/home", f"Failed to navigate to home page. Current URL: {page.url}"

@pytest.fixture(scope="session")
def logged_in_browser_context():
    gpage = gen_page()
    gserver_url = gen_flask_server()
    page = next(gpage)
    server_url = next(gserver_url)
    login_action(page, server_url)
    yield (page, server_url)
    gpage.close()
    gserver_url.close()
