import requests
import json
import os
import config

BASE_URL = config.TARGET_URL.rstrip('/')
EMAIL = config.TARGET_EMAIL
PASSWORD = config.TARGET_PASSWORD

# Ищем любое фото для теста
IMAGE_PATH = None
if os.path.exists(config.IMAGES_DIR):
    for f in os.listdir(config.IMAGES_DIR):
        if f.endswith('.webp') or f.endswith('.jpg'):
            IMAGE_PATH = os.path.join(config.IMAGES_DIR, f)
            break

print(f"Using image: {IMAGE_PATH}")

def login():
    session = requests.Session()
    login_url = f"{BASE_URL}/auth/sign_in"
    payload = {"email": EMAIL, "password": PASSWORD}
    try:
        resp = session.post(login_url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        token = data.get('data', {}).get('access_token') or data.get('access_token')
        uid = data.get('data', {}).get('uid') or resp.headers.get('uid')
        client = data.get('data', {}).get('client') or resp.headers.get('client')
        
        session.headers.update({
            'access-token': token,
            'client': client,
            'uid': uid
        })
        return session, data.get('data', {}).get('id')
    except Exception as e:
        print(f"Login failed: {e}")
        return None, None

def test_upload(session, account_id, key_format):
    print(f"\nTesting format: {key_format}")
    url = f"{BASE_URL}/api/v1/accounts/{account_id}/products"
    
    # Minimal product
    form_data = {
        'product[name][ru]': f'Test Img {key_format}',
        'product[price]': '100',
        'product[quantity]': '1',
        'product[is_published]': 'true'
    }
    
    files = {}
    if IMAGE_PATH and os.path.exists(IMAGE_PATH):
        f = open(IMAGE_PATH, 'rb')
        key = key_format.replace('{i}', '0')
        files[key] = (os.path.basename(IMAGE_PATH), f, 'image/jpeg')
        
        try:
            resp = session.post(url, data=form_data, files=files)
            if resp.status_code in [200, 201]:
                print(f"✅ Success! ID={resp.json().get('id')}")
            else:
                print(f"❌ Failed: {resp.status_code} {resp.text[:100]}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            f.close()

def main():
    session, account_id = login()
    if not session: return
    
    # Список форматов для проверки
    formats = [
        'product[images_attributes][{i}][image]', 
        'product[images_attributes][{i}][file]',
        'product[images_attributes][][image]',
        'product[attachments][{i}]',
        'product[attachments][]',
        'product[images][{i}]',
        'product[images][]'
    ]
    
    for fmt in formats:
        test_upload(session, account_id, fmt)

if __name__ == "__main__":
    main()
