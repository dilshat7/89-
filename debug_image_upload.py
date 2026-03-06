import requests
import json
import os
import config

# Setup
BASE_URL = config.TARGET_URL.rstrip('/')
EMAIL = config.TARGET_EMAIL
PASSWORD = config.TARGET_PASSWORD
IMAGE_PATH = r"C:\Users\ddjab\product-transfer\data\images\product_1_1.webp"

if not os.path.exists(IMAGE_PATH):
    # Try to find any jpg/webp in data/images
    for f in os.listdir(r"C:\Users\ddjab\product-transfer\data\images"):
        if f.endswith('.webp') or f.endswith('.jpg'):
            IMAGE_PATH = os.path.join(r"C:\Users\ddjab\product-transfer\data\images", f)
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
        token = None
        account_id = None
        
        if 'data' in data:
            token = data['data'].get('access_token')
            account_id = data['data'].get('account_id')
        else:
            token = data.get('access_token')
            account_id = data.get('account_id') or data.get('current_account_id')
            
        if 'access-token' in resp.headers:
            session.headers.update({
                'access-token': resp.headers.get('access-token'),
                'client': resp.headers.get('client'),
                'uid': resp.headers.get('uid')
            })
        elif token:
            session.headers.update({'Authorization': f'Bearer {token}'})
            
        return session, account_id
    except Exception as e:
        print(f"Login failed: {e}")
        return None, None

def test_upload(session, account_id, key_format):
    print(f"\nTesting format: {key_format}")
    
    url = f"{BASE_URL}/api/v1/accounts/{account_id}/products"
    
    form_data = {
        'product[name][ru]': f'Debug Image {key_format}',
        'product[price]': '100',
        'product[quantity]': '1',
        'product[is_published]': 'true'
    }
    
    files = {}
    f = open(IMAGE_PATH, 'rb')
    
    # Replace placeholder with index 0
    key = key_format.replace('{i}', '0')
    files[key] = (os.path.basename(IMAGE_PATH), f, 'image/webp')
    
    try:
        resp = session.post(url, data=form_data, files=files)
        print(f"Status: {resp.status_code}")
        if resp.status_code in [200, 201]:
            data = resp.json()
            print(f"Product created: ID={data.get('id')}")
            # Check if image present in response
            # Adjust this check based on actual response structure
            if 'image' in data and data['image']:
                 print("✅ Image found in response field 'image'")
            elif 'images' in data and len(data['images']) > 0:
                 print("✅ Image found in response field 'images'")
            elif 'attachments' in data and len(data['attachments']) > 0:
                 print("✅ Image found in response field 'attachments'")
            else:
                 print("⚠️ Product created but image might be missing in response")
                 print(f"Response keys: {list(data.keys())}")
        else:
            print(f"Failed: {resp.text[:200]}")
    except Exception as e:
         print(f"Error: {e}")
    finally:
        f.close()

def main():
    session, account_id = login()
    if not session:
        return
        
    formats = [
        'product[images_attributes][{i}][attachment]',
        'product[images_attributes][{i}][image]',
        'product[images_attributes][{i}][file]',
        'product[image][{i}]', 
        'product[images][{i}]',
        'product[attachments][{i}]',
        'product[file]',
        'image',
        'file'
    ]
    
    for fmt in formats:
        test_upload(session, account_id, fmt)

if __name__ == "__main__":
    main()
