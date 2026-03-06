import requests
import config

class ProductCleaner:
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
                print(f"❌ Не получен токен. Response: {data}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка авторизации: {e}")
            return False
    
    def get_all_products(self):
        print("\nПолучение списка товаров...")
        
        products_url = f"{self.base_url}/api/v1/accounts/{self.account_id}/products"
        
        try:
            response = self.session.get(products_url)
            response.raise_for_status()
            
            data = response.json()
            products = data.get('data', [])
            
            print(f"Найдено товаров: {len(products)}")
            return products
            
        except Exception as e:
            print(f"❌ Ошибка получения товаров: {e}")
            return []
    
    def delete_product(self, product_id):
        delete_url = f"{self.base_url}/api/v1/accounts/{self.account_id}/products/{product_id}"
        
        try:
            response = self.session.delete(delete_url)
            response.raise_for_status()
            return True
            
        except Exception as e:
            print(f"  ❌ Ошибка удаления товара {product_id}: {e}")
            return False
    
    def delete_all_products(self):
        products = self.get_all_products()
        
        if not products:
            print("Товары не найдены.")
            return
        
        print(f"\n🗑️  Удаление {len(products)} товаров...\n")
        
        deleted = 0
        failed = 0
        
        for i, product in enumerate(products, 1):
            product_id = product.get('id')
            product_name = product.get('name', 'Unknown')
            
            print(f"[{i}/{len(products)}] Удаление: {product_name} (ID: {product_id})...", end=" ")
            
            if self.delete_product(product_id):
                print("✅")
                deleted += 1
            else:
                print("❌")
                failed += 1
        
        print(f"\n{'='*50}")
        print(f"✅ Удаление завершено!")
        print(f"   Удалено: {deleted}")
        print(f"   Ошибок: {failed}")
        print(f"{'='*50}")
    
    def get_all_categories(self):
        print("\nПолучение списка категорий...")
        
        categories_url = f"{self.base_url}/api/v1/accounts/{self.account_id}/categories"
        
        try:
            response = self.session.get(categories_url)
            response.raise_for_status()
            
            data = response.json()
            categories = data.get('data', [])
            
            print(f"Найдено категорий: {len(categories)}")
            return categories
            
        except Exception as e:
            print(f"❌ Ошибка получения категорий: {e}")
            return []
    
    def delete_category(self, category_id):
        delete_url = f"{self.base_url}/api/v1/accounts/{self.account_id}/categories/{category_id}"
        
        try:
            response = self.session.delete(delete_url)
            response.raise_for_status()
            return True
            
        except Exception as e:
            print(f"  ❌ Ошибка удаления категории {category_id}: {e}")
            return False
    
    def delete_all_categories(self):
        categories = self.get_all_categories()
        
        if not categories:
            print("Категории не найдены.")
            return
        
        print(f"\n🗑️  Удаление {len(categories)} категорий...\n")
        
        deleted = 0
        failed = 0
        
        for i, category in enumerate(categories, 1):
            category_id = category.get('id')
            category_name = category.get('name', 'Unknown')
            
            print(f"[{i}/{len(categories)}] Удаление: {category_name} (ID: {category_id})...", end=" ")
            
            if self.delete_category(category_id):
                print("✅")
                deleted += 1
            else:
                print("❌")
                failed += 1
        
        print(f"\n{'='*50}")
        print(f"✅ Удаление завершено!")
        print(f"   Удалено: {deleted}")
        print(f"   Ошибок: {failed}")
        print(f"{'='*50}")
    
    def clean_all(self):
        if not self.login():
            return
        
        print("\n" + "="*50)
        print("ОЧИСТКА ВСЕХ ДАННЫХ")
        print("="*50)
        
        self.delete_all_products()
        
        print("\n")
        
        self.delete_all_categories()

def main():
    cleaner = ProductCleaner()
    
    print("\n⚠️  ВНИМАНИЕ: Эта операция удалит ВСЕ товары и категории!")
    confirmation = input("Вы уверены? Введите 'да' для продолжения: ")
    
    if confirmation.lower() in ['да', 'yes', 'y']:
        cleaner.clean_all()
    else:
        print("❌ Операция отменена.")

if __name__ == "__main__":
    main()
