import pytest
import os
import json

def test_login_cookies(page, flask_server):
    """Test that cookies are set correctly after login."""
    # Navigate to login page
    page.goto(f"{flask_server}/login")
    
    # Get the master password from the app
    test_password = os.getenv("LITEFLOW_LOGIN_PASSWORD")
    
    # Fill in login form with correct password and submit
    page.fill("#password", test_password)
    page.click("button.btn-primary")
    
    # Wait for navigation to complete
    page.wait_for_url(f"{flask_server}/home")
    
    # Check that we're on the home page
    assert page.url == f"{flask_server}/home"
    
    # Get cookies
    cookies = page.context.cookies()
    
    # Check for JWT cookies
    access_token_cookie = next((c for c in cookies if c["name"] == "access_token_cookie"), None)
    refresh_token_cookie = next((c for c in cookies if c["name"] == "refresh_token_cookie"), None)
    
    # Verify cookies exist
    assert access_token_cookie is not None, "access_token_cookie not found"
    assert refresh_token_cookie is not None, "refresh_token_cookie not found"
    
    # Verify cookie properties
    assert access_token_cookie["httpOnly"] is True, "access_token_cookie should be httpOnly"
    assert refresh_token_cookie["httpOnly"] is True, "refresh_token_cookie should be httpOnly"
    
    print(f"Cookies after login: {json.dumps(cookies, indent=2)}")

def test_no_cookies_with_incorrect_password(page, flask_server):
    """Test that no JWT cookies are set with incorrect password."""
    # Navigate to login page
    page.goto(f"{flask_server}/login")
    
    # Fill in login form with incorrect password and submit
    page.fill("#password", "wrong_password")
    page.click("button.btn-primary")
    
    # Check that we're still on the login page
    assert page.url == f"{flask_server}/login"
    
    # Get cookies
    cookies = page.context.cookies()
    
    # Check that no JWT cookies exist
    access_token_cookie = next((c for c in cookies if c["name"] == "access_token_cookie"), None)
    refresh_token_cookie = next((c for c in cookies if c["name"] == "refresh_token_cookie"), None)
    
    assert access_token_cookie is None, "access_token_cookie should not be set"
    assert refresh_token_cookie is None, "refresh_token_cookie should not be set"
