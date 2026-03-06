import json
import os
import time
from pathlib import Path
import requests
import config


class ProductUploader:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = config.TARGET_URL.rstrip('/')
        self.account_id = None
        self.token = None
        
    def login(self):
        """Авторизация и получение токена"""
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
            
            # API возвращает токен в data.access_token
            if 'data' in data:
                inner_data = data['data']
                self.token = inner_data.get('access_token')
                self.account_id = inner_data.get('account_id')
            else:
                self.token = data.get('access_token') or data.get('token')
                self.account_id = data.get('current_account_id') or data.get('account_id')
            
            # API использует devise_token_auth - нужны заголовки из response
            if 'access-token' in response.headers:
                self.session.headers.update({
                    'access-token': response.headers.get('access-token'),
                    'client': response.headers.get('client'),
                    'uid': response.headers.get('uid')
                })
                print(f"✅ Авторизация успешна (Account ID: {self.account_id})")
                return True
            elif self.token:
                # Fallback на Bearer если нет devise заголовков
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}'
                })
                print(f"✅ Авторизация успешна (Account ID: {self.account_id})")
                return True
            else:
                print(f"❌ Не получен токен. Response: {data}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка авторизации: {e}")
            return False
    
    def get_categories(self):
        """Получение списка категорий"""
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/product_categories"
        
        try:
            response = self.session.get(url, params={'per_page': 100})
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, list) else data.get('data', [])
        except Exception as e:
            print(f"❌ Ошибка получения категорий: {e}")
            return []
    
    
    def create_category(self, category_name, parent_id=None):
        """Создание категории с опциональным parent_id"""
        print(f"Создание категории: {category_name} (parent_id={parent_id})")
        
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/product_categories"
        
        payload = {
            "name": {
                "en": category_name,
                "ru": category_name,
                "uz": category_name,
                "uz_cyr": category_name
            }
        }
        
        if parent_id:
            payload["parent_id"] = parent_id
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            category_data = response.json()
            category_id = category_data.get('id')
            print(f"✅ Категория создана: ID={category_id}")
            return category_data
        except Exception as e:
            print(f"❌ Ошибка создания категории: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"   Response: {e.response.text}")
            return None
    
    def ensure_parent_category(self, parent_name):
        """Создание или получение родительской категории"""
        categories = self.get_categories()
        
        for cat in categories:
            cat_name = cat.get('name', {})
            if isinstance(cat_name, dict):
                cat_name = cat_name.get('ru', '')
            if cat_name == parent_name and not cat.get('parent_id'):
                print(f"✅ Родительская категория '{parent_name}' уже существует (ID={cat.get('id')})")
                return cat.get('id')
        
        category = self.create_category(parent_name, parent_id=None)
        return category.get('id') if category else None
    
    def ensure_child_category(self, category_name, parent_id):
        """Создание или получение дочерней категории"""
        categories = self.get_categories()
        
        for cat in categories:
            cat_name = cat.get('name', {})
            if isinstance(cat_name, dict):
                cat_name = cat_name.get('ru', '')
            if cat_name == category_name and cat.get('parent_id') == parent_id:
                print(f"✅ Дочерняя категория '{category_name}' уже существует (ID={cat.get('id')})")
                return cat.get('id')
        
        category = self.create_category(category_name, parent_id=parent_id)
        return category.get('id') if category else None
    
    def create_product(self, product_data, category_id):
        """Создание товара через FormData"""
        title = product_data.get('title', 'Товар без названия')[:50]
        print(f"Создание товара: {title}...", end=" ")
        
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/products"
        
        # Descriptions
        desc_ru = product_data.get('description', '')
        desc_en = product_data.get('description_en', '')
        desc_uz = product_data.get('description_uz', '')
        desc_uz_cyr = product_data.get('description_uz_cyr', '')
        
        # Fallbacks
        if not desc_ru: desc_ru = f"Качественный товар"
        if not desc_en: desc_en = desc_ru
        if not desc_uz: desc_uz = desc_ru
        if not desc_uz_cyr: desc_uz_cyr = desc_uz
        
        # Prepare Form Data
        form_data = {
            'product[name][en]': product_data.get('title_en', title),
            'product[name][ru]': title,
            'product[name][uz]': product_data.get('title_uz', title),
            'product[name][uz_cyr]': product_data.get('title_uz_cyr', title),
            
            'product[description][en]': desc_en,
            'product[description][ru]': desc_ru,
            'product[description][uz]': desc_uz,
            'product[description][uz_cyr]': desc_uz_cyr,
            
            'product[product_category_id]': str(category_id),
            'product[quantity]': str(product_data.get('quantity', 100)),
            'product[track_quantity]': 'true',
            'product[is_published]': 'true',
            'product[prices_attributes][0][price]': str(self._extract_price(product_data['price'])),
            'product[prices_attributes][0][currency_code]': 'UZS',
        }
        
        # Используем список для files, чтобы поддерживать одинаковые ключи
        files = []
        opened_files = []
        
        local_images = product_data.get('local_images', [])
        if not local_images and product_data.get('local_image'):
             local_images = [product_data['local_image']]
             
        # Правильный формат для множественных изображений (список кортежей)
        for i, image_path in enumerate(local_images):
            if os.path.exists(image_path):
                f = open(image_path, 'rb')
                opened_files.append(f)
                # Ключ 'product[images][]' повторяется для каждого файла
                files.append(('product[images][]', (
                    os.path.basename(image_path),
                    f,
                    'image/jpeg'
                )))
        
        print(f"({len(opened_files)} фото)", end=" ")
        
        try:
            response = self.session.post(url, data=form_data, files=files)
            
            if response.status_code != 200 and response.status_code != 201:
                print(f"❌ Ошибка {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                return None
            
            product = response.json()
            product_id = product.get('id')
            print(f"✅ ID={product_id}")
            return product
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
        finally:
            for f in opened_files:
                f.close()
    
    def _extract_price(self, price_str):
        """Извлечение цены из строки"""
        import re
        if isinstance(price_str, (int, float)):
            return int(price_str)
        numbers = re.findall(r'\d+', str(price_str).replace(' ', ''))
        return int(''.join(numbers)) if numbers else 10000
    
    def upload_products_from_json(self, json_path, limit=None):
        """Загрузка товаров из JSON"""
        if not os.path.exists(json_path):
            print(f"❌ Файл не найден: {json_path}")
            return
        
        with open(json_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        if limit:
            products = products[:limit]
        
        print(f"\n📦 Загрузка {len(products)} товаров...")
        
        
        # 1. Загружаем существующие категории
        print("Получение существующих категорий...")
        existing_categories = self.get_categories()
        
        # Карта: {name: id}
        categories_map = {}
        for cat in existing_categories:
            cat_id = cat['id']
            # Извлекаем имя на RU
            name_obj = cat.get('name', {})
            name = name_obj.get('ru') or name_obj.get('en') or list(name_obj.values())[0] if isinstance(name_obj, dict) else str(name_obj)
            categories_map[name.strip()] = cat_id
                
        # 2. Создаем ТОЛЬКО родительские категории ("Мужчины", "Женщины")
        required_parents = ["Мужчины", "Женщины"]
        for p_name in required_parents:
            if p_name not in categories_map:
                cat = self.create_category(p_name)
                if cat:
                    categories_map[p_name] = cat['id']
            else:
                print(f"Категория '{p_name}' уже существует.")

        print(f"\n{'='*60}")
        print(f"Начало загрузки товаров (строго в Мужчины/Женщины)...")
        print(f"{'='*60}")
        
        uploaded = 0
        failed = 0
        
        for i, product in enumerate(products, 1):
            title = product.get('title', 'Unknown')[:40]
            gender = product.get('gender', '').lower()
            
            # Определяем категорию ТОЛЬКО по полу
            if 'муж' in gender:
                target_category_name = "Мужчины"
            elif 'жен' in gender:
                target_category_name = "Женщины"
            else:
                target_category_name = "Мужчины" # Fallback
            
            print(f"[{i}/{len(products)}] {title} -> {target_category_name}...", end=" ")
            
            category_id = categories_map.get(target_category_name)
            if not category_id:
                print(f"❌ Категория '{target_category_name}' не найдена (ошибка создания)")
                failed += 1
                continue
            
            # Загружаем товар прямо в категорию пола
            result = self.create_product(product, category_id)
            
            if result:
                uploaded += 1
                print("✅")
            else:
                failed += 1
                print("❌")
            
            time.sleep(0.5)
        
        print(f"\n{'='*60}")
        print(f"✅ Загрузка завершена!")
        print(f"   Успешно: {uploaded}")
        print(f"   Ошибки: {failed}")
        print(f"{'='*50}")


def main():
    uploader = ProductUploader()
    
    if not uploader.login():
        return
    
    uploader.upload_products_from_json(config.PRODUCTS_JSON)


if __name__ == "__main__":
    main()
