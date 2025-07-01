#!/usr/bin/env python3
"""
LinkedIn OAuth 2.0 Access Token Generator
Step-by-step guide to get your LinkedIn API access token
"""

import os
import urllib.parse
import requests
import webbrowser
from dotenv import load_dotenv

load_dotenv()

def step1_check_setup():
    """Check if LinkedIn app is properly configured"""
    
    client_id = os.getenv("LINKEDIN_CLIENT_ID")
    client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
    
    print("🔑 LinkedIn Access Token Generator")
    print("=" * 50)
    
    print("📋 Prerequisites Check:")
    print(f"✅ Client ID: {client_id}")
    print(f"✅ Client Secret: {client_secret[:10]}...")
    
    redirect_uri = "http://localhost:8080/callback"
    
    print(f"\n🔧 IMPORTANT: Configure your LinkedIn app")
    print(f"1. Go to: https://developer.linkedin.com/")
    print(f"2. Open your LinkedIn app")
    print(f"3. Go to 'Auth' tab")
    print(f"4. Add this redirect URI: {redirect_uri}")
    print(f"5. Save changes")
    
    ready = input("\n✅ Have you added the redirect URI to your LinkedIn app? (y/n): ")
    return ready.lower() == 'y', client_id, client_secret, redirect_uri

def step2_get_authorization_url(client_id, redirect_uri):
    """Generate authorization URL and open in browser"""
    
    print(f"\n🌐 Step 2: Get Authorization")
    print("=" * 30)
    
    # Define scopes for job access
    scopes = [
        'r_liteprofile',
        'r_emailaddress', 
        'w_member_social'
    ]
    
    scope_string = ' '.join(scopes)
    
    # Generate state for security
    import secrets
    state = secrets.token_urlsafe(16)
    
    auth_params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'state': state,
        'scope': scope_string
    }
    
    auth_url = 'https://www.linkedin.com/oauth/v2/authorization?' + urllib.parse.urlencode(auth_params)
    
    print("🔗 Authorization URL:")
    print(auth_url)
    
    # Try to open browser
    try:
        webbrowser.open(auth_url)
        print("\n✅ Browser opened automatically")
    except:
        print("\n⚠️  Please copy the URL above and open it manually")
    
    print(f"\n📋 Instructions:")
    print(f"1. LinkedIn will ask you to sign in and authorize")
    print(f"2. After clicking 'Allow', you'll be redirected to:")
    print(f"   {redirect_uri}?code=YOUR_CODE&state={state}")
    print(f"3. The page will show an error (that's normal!)")
    print(f"4. Copy the 'code' parameter from the URL bar")
    
    return state

def step3_exchange_for_token(auth_code, client_id, client_secret, redirect_uri):
    """Exchange authorization code for access token"""
    
    print(f"\n🔄 Step 3: Get Access Token")
    print("=" * 30)
    
    token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
    
    token_data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    print("📡 Exchanging code for token...")
    
    try:
        response = requests.post(token_url, data=token_data, headers=headers)
        
        if response.status_code == 200:
            token_info = response.json()
            access_token = token_info.get('access_token')
            expires_in = token_info.get('expires_in', 'Unknown')
            
            print("✅ SUCCESS! Access token received")
            print(f"   Token: {access_token[:30]}...")
            print(f"   Expires in: {expires_in} seconds")
            
            return access_token
        else:
            print(f"❌ Token request failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def step4_save_token(access_token):
    """Save access token to .env file"""
    
    print(f"\n💾 Step 4: Save Token")
    print("=" * 20)
    
    # Read .env file
    env_lines = []
    token_found = False
    
    try:
        with open('.env', 'r') as f:
            env_lines = f.readlines()
    except FileNotFoundError:
        pass
    
    # Update or add token line
    updated_lines = []
    for line in env_lines:
        if line.startswith('LINKEDIN_ACCESS_TOKEN='):
            updated_lines.append(f'LINKEDIN_ACCESS_TOKEN={access_token}\n')
            token_found = True
        else:
            updated_lines.append(line)
    
    if not token_found:
        updated_lines.append(f'LINKEDIN_ACCESS_TOKEN={access_token}\n')
    
    # Write back to file
    with open('.env', 'w') as f:
        f.writelines(updated_lines)
    
    print("✅ Token saved to .env file")

def step5_test_token(access_token):
    """Test the access token"""
    
    print(f"\n🧪 Step 5: Test Token")
    print("=" * 20)
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Test basic profile endpoint
    try:
        response = requests.get('https://api.linkedin.com/v2/people/~', headers=headers)
        
        if response.status_code == 200:
            profile = response.json()
            first_name = profile.get('localizedFirstName', 'Unknown')
            last_name = profile.get('localizedLastName', 'Unknown')
            print(f"✅ Token works! Hello {first_name} {last_name}")
            return True
        else:
            print(f"⚠️  Token test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    """Main function to run the complete OAuth flow"""
    
    print("🚀 LinkedIn API Access Token Setup")
    print("=" * 60)
    
    # Step 1: Check setup
    ready, client_id, client_secret, redirect_uri = step1_check_setup()
    
    if not ready:
        print("\n⚠️  Please configure your LinkedIn app first")
        print("   Then run this script again")
        return
    
    if not client_id or not client_secret:
        print("\n❌ Missing LinkedIn credentials in .env file")
        return
    
    # Step 2: Get authorization
    state = step2_get_authorization_url(client_id, redirect_uri)
    
    # Get code from user
    print(f"\n📝 Enter the authorization code:")
    auth_code = input("Code: ").strip()
    
    if not auth_code:
        print("❌ No code provided")
        return
    
    # Step 3: Exchange for token
    access_token = step3_exchange_for_token(auth_code, client_id, client_secret, redirect_uri)
    
    if not access_token:
        print("❌ Failed to get access token")
        return
    
    # Step 4: Save token
    step4_save_token(access_token)
    
    # Step 5: Test token
    if step5_test_token(access_token):
        print(f"\n🎉 SUCCESS! You now have LinkedIn API access")
        print(f"   You can now run: python jobs_api_integration.py")
    else:
        print(f"\n⚠️  Token saved but test failed")
        print(f"   Check your LinkedIn app permissions")

if __name__ == "__main__":
    main()
    
    if not auth_code:
        print("❌ No authorization code provided")
        return None
    
    # Step 3: Exchange code for access token
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    print("🔄 Exchanging authorization code for access token...")
    
    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        access_token = token_data.get('access_token')
        
        if access_token:
            print("✅ Success! Your access token:")
            print(f"📋 {access_token}")
            print()
            print("💾 Add this to your .env file:")
            print(f"LINKEDIN_ACCESS_TOKEN={access_token}")
            
            # Test the token
            test_token(access_token)
            
            return access_token
        else:
            print("❌ No access token in response")
            print(f"📋 Response: {token_data}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Token request failed: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"📋 Error response: {e.response.text}")
    
    return None

def test_token(access_token):
    """Test the access token by making a basic API call"""
    
    print("🧪 Testing access token...")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Test with basic profile endpoint
    test_url = "https://api.linkedin.com/v2/me"
    
    try:
        response = requests.get(test_url, headers=headers)
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ Token works! Profile: {profile.get('localizedFirstName', 'N/A')} {profile.get('localizedLastName', 'N/A')}")
        else:
            print(f"⚠️  Token test failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️  Token test error: {e}")

def check_job_api_access():
    """Check if we have access to job-related APIs"""
    
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    if not access_token or access_token == "your_access_token":
        print("❌ No valid access token found")
        return False
    
    print("🎯 Testing Job API access...")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Try different job-related endpoints
    test_endpoints = [
        ("Basic Profile", "https://api.linkedin.com/v2/me"),
        ("Company Search", "https://api.linkedin.com/v2/companies"),
        ("Job Search", "https://api.linkedin.com/v2/jobSearchResults"),
    ]
    
    for name, url in test_endpoints:
        try:
            response = requests.get(url, headers=headers)
            print(f"   {name}: {response.status_code} - {'✅ OK' if response.status_code == 200 else '❌ Failed'}")
            if response.status_code != 200:
                print(f"      Error: {response.text[:100]}...")
        except Exception as e:
            print(f"   {name}: ❌ Error - {e}")
    
    return True

def main():
    """Main function"""
    
    print("🚀 LinkedIn API Access Token Helper")
    print("=" * 60)
    
    # Check current token
    current_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    if current_token and current_token != "your_access_token":
        print(f"🔍 Current token: {current_token[:20]}...")
        print("✅ You already have a token. Testing it...")
        test_token(current_token)
        print()
        
        choice = input("💭 Do you want to get a new token? (y/N): ").strip().lower()
        if choice not in ['y', 'yes']:
            check_job_api_access()
            return
    
    # Get new token
    print("\n🔄 Getting new access token...")
    print("📋 Prerequisites:")
    print("   1. LinkedIn Developer Account")
    print("   2. LinkedIn App created at https://developer.linkedin.com/")
    print("   3. Client ID and Secret in .env file")
    print()
    
    proceed = input("💭 Ready to proceed? (y/N): ").strip().lower()
    if proceed in ['y', 'yes']:
        get_linkedin_access_token()
    else:
        print("ℹ️  Visit https://developer.linkedin.com/ to create an app first")

if __name__ == "__main__":
    main()
