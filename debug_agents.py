import requests
import config

BASE_URL = config.TARGET_URL.rstrip('/')
EMAIL = config.TARGET_EMAIL
PASSWORD = config.TARGET_PASSWORD

def login():
    session = requests.Session()
    login_url = f"{BASE_URL}/auth/sign_in"
    payload = {"email": EMAIL, "password": PASSWORD}
    try:
        resp = session.post(login_url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        headers = {
            'access-token': data['data'].get('access_token') or resp.headers.get('access-token'),
            'client': data['data'].get('client') or resp.headers.get('client'),
            'uid': data['data'].get('uid') or resp.headers.get('uid')
        }
        account_id = data['data']['id']  # Usually user ID, but we need Account ID
        # Sometimes Account ID is different. Let's list accounts if possible or use config.
        # But for now assuming account_id from login is what we need or we find it.
        # Chatwoot-like API usually returns data.data.accounts or similar.
        
        # Let's try to find account_id from /api/v1/profile if available
        return session, headers, account_id
    except Exception as e:
        print(f"Login failed: {e}")
        return None, None, None

def check_agents_api():
    session, headers, user_id = login()
    if not session: return

    # Try to find correct Account ID. Usually it's in the response of sign_in under 'accounts'
    # But let's assume account_id=1 or try to list profile.
    
    # Try getting profile to find accounts
    try:
        resp = session.get(f"{BASE_URL}/api/v1/profile", headers=headers)
        if resp.status_code == 200:
            accounts = resp.json().get('accounts', [])
            if accounts:
                account_id = accounts[0]['id']
                print(f"✅ Found Account ID: {account_id}")
            else:
                print("❌ No accounts found in profile. Using login ID.")
                account_id = user_id
        else:
            print(f"⚠️ Profile check failed ({resp.status_code}). Using login ID: {user_id}")
            account_id = user_id
    except:
        account_id = user_id

    api_url = f"{BASE_URL}/api/v1/accounts/{account_id}/agents"
    print(f"\nChecking API: {api_url}")
    
    # 1. List Agents
    try:
        resp = session.get(api_url, headers=headers)
        if resp.status_code == 200:
            agents = resp.json()
            print(f"✅ Agents List Success! Found {len(agents)} agents.")
            for a in agents:
                print(f"   - {a.get('name')} ({a.get('email')}) [{a.get('role')}]")
        else:
            print(f"❌ List Agents Failed: {resp.status_code} {resp.text}")
            return
    except Exception as e:
        print(f"Error listing agents: {e}")
        return

    # 2. Try Create Demo Agent (Dry Run - usually creates real one, so we just check POST availability or ask user)
    print("\nTo create an agent, we need:")
    print("- Name")
    print("- Email")
    print("- Role (agent/administrator)")
    
    print("API seems accessible. Ready to automate.")

if __name__ == "__main__":
    check_agents_api()
