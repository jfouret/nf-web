import pytest
import os

# List of protected routes to test
PROTECTED_ROUTES = [
    "/",  # Home page
    "/home",
    "/pipelines",
    "/import_pipeline",
    "/configs",
    "/run_configs",
    "/storage"
]

@pytest.mark.parametrize("route", PROTECTED_ROUTES)
def test_protected_routes_redirect_to_login(browser_context, route):
    """Test that protected routes redirect to login page when not logged in."""
    # Unpack the browser context
    page, server_url = browser_context
    
    # Navigate to protected route
    page.goto(f"{server_url}{route}")
    
    # Check that we're redirected to the login page
    page.wait_for_url(f"{server_url}/login", timeout=5000)
    assert page.url == f"{server_url}/login"

def test_access_protected_routes_after_login(logged_in_browser_context):
    """Test that protected routes are accessible after login."""
    # Unpack the browser context
    page, server_url = logged_in_browser_context
    
    # Test each protected route
    for route in PROTECTED_ROUTES:
        # Navigate to protected route
        page.goto(f"{server_url}{route}")
        
        # Special case for root route which redirects to /home
        if route == "/":
            # Check that we're redirected to home, not to login
            assert page.url == f"{server_url}/home"
        else:
            # Check that we're not redirected to login
            assert page.url == f"{server_url}{route}"
