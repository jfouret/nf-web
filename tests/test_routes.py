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
def test_protected_routes_redirect_to_login(page, flask_server, route):
    """Test that protected routes redirect to login page when not logged in."""
    # Navigate to protected route
    page.goto(f"{flask_server}{route}")
    
    # Check that we're redirected to the login page
    page.wait_for_url(f"{flask_server}/login", timeout=5000)
    assert page.url == f"{flask_server}/login"

def test_access_protected_routes_after_login(logged_in_page, flask_server):
    """Test that protected routes are accessible after login."""
    # Test each protected route
    for route in PROTECTED_ROUTES:
        # Navigate to protected route
        logged_in_page.goto(f"{flask_server}{route}")
        
        # Special case for root route which redirects to /home
        if route == "/":
            # Check that we're redirected to home, not to login
            assert logged_in_page.url == f"{flask_server}/home"
        else:
            # Check that we're not redirected to login
            assert logged_in_page.url == f"{flask_server}{route}"
