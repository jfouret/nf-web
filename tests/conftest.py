import subprocess

def ensure_firefox_installed():
    """Ensure Firefox browser is installed for Playwright."""
    print("Ensuring Firefox browser is installed for Playwright...")
    subprocess.run(["python", "-m", "playwright", "install", "firefox"], check=True)

ensure_firefox_installed()

from tests.fixtures.base import *
from tests.fixtures.loaded import *
