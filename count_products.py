import requests
import config

class ProductCounter:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = config.TARGET_URL.rstrip('/')
        self.account_id = None
        
    def login(self):
        print("Авторизация...")
        
        login_url = f"{self.base_url}/auth/sign_in"
        
        payload = {
            "email": config.TARGET_EMAIL,
            "password": config.TARGET_PASSWORD
        }
        
        try:
            response = self.session.post(login_url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' in data:
                inner_data = data['data']
                self.account_id = inner_data.get('account_id')
            else:
                self.account_id = data.get('current_account_id') or data.get('account_id')
            
            if 'access-token' in response.headers:
                self.session.headers.update({
                    'access-token': response.headers.get('access-token'),
                    'client': response.headers.get('client'),
                    'uid': response.headers.get('uid')
                })
                print(f"✅ Авторизация успешна (Account ID: {self.account_id})")
                return True
            else:
                print(f"❌ Не получен токен")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка авторизации: {e}")
            return False
    
    def get_products_count(self):
        print("\nПолучение информации о товарах...")
        
        products_url = f"{self.base_url}/api/v1/accounts/{self.account_id}/products"
        
        try:
            response = self.session.get(products_url)
            response.raise_for_status()
            
            data = response.json()
            products = data.get('data', [])
            
            print(f"\n{'='*50}")
            print(f"📦 Всего товаров в системе: {len(products)}")
            print(f"{'='*50}\n")
            
            # Группировка по категориям
            categories = {}
            for product in products:
                cat_id = product.get('category_id', 'Без категории')
                cat_name = product.get('category', {}).get('name', f'ID:{cat_id}')
                
                if cat_name not in categories:
                    categories[cat_name] = 0
                categories[cat_name] += 1
            
            print("По категориям:")
            for cat_name, count in sorted(categories.items(), key=lambda x: -x[1]):
                print(f"  • {cat_name}: {count} товаров")
            
            return len(products)
            
        except Exception as e:
            print(f"❌ Ошибка получения товаров: {e}")
            return 0

def main():
    counter = ProductCounter()
    
    if counter.login():
        counter.get_products_count()

if __name__ == "__main__":
    main()
