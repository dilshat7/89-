import json
import os
import time
import re
from pathlib import Path
from playwright.sync_api import sync_playwright
import requests
from deep_translator import GoogleTranslator
import config

class TerraProScraper:
    def __init__(self):
        self.products = []
        self.translators = {
            'en': GoogleTranslator(source='auto', target='en'),
            'uz': GoogleTranslator(source='auto', target='uz'),  # Latin
        }
        
    def latin_to_cyrillic(self, text):
        """Convert Uzbek Latin to Cyrillic"""
        mapping = {
            'sh': 'ш', 'ch': 'ч', "o'": 'ў', "g'": 'ғ',
            'a': 'а', 'b': 'б', 'd': 'д', 'e': 'е', 'f': 'ф',
            'g': 'г', 'h': 'ҳ', 'i': 'и', 'j': 'ж', 'k': 'к',
            'l': 'л', 'm': 'м', 'n': 'н', 'o': 'о', 'p': 'п',
            'q': 'қ', 'r': 'р', 's': 'с', 't': 'т', 'u': 'у',
            'v': 'в', 'x': 'х', 'y': 'й', 'z': 'з',
        }
        result = text.lower()
        # Apply mapping (longest patterns first)
        for lat, cyr in sorted(mapping.items(), key=lambda x: -len(x[0])):
            result = result.replace(lat, cyr)
        return result
    
    def translate_text(self, text, target_lang):
        if not text:
            return ""
        try:
            if target_lang == 'uz-cyr':
                # Translate to Latin Uzbek first
                uz_latin = self.translators['uz'].translate(text)
                # Convert to Cyrillic
                return self.latin_to_cyrillic(uz_latin)
            else:
                return self.translators[target_lang].translate(text)
        except Exception as e:
            print(f"Translation error ({target_lang}): {e}")
            return text

    def clean_price(self, price_str):
        return ''.join(filter(str.isdigit, price_str))

    def scrape_products(self, categories_dict, parent_category, gender):
        print(f"\nПарсинг товаров: {parent_category} ({gender})...")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            total_collected = 0
            
            for category_name, category_url in categories_dict.items():
                print(f"\n{'='*60}")
                print(f"Категория: {category_name}")
                print(f"URL: {category_url}")
                print(f"{'='*60}")
                
                try:
                    page.goto(category_url, wait_until="domcontentloaded", timeout=60000)
                except Exception as e:
                    print(f"❌ Ошибка перехода в категорию: {e}")
                    continue

                time.sleep(2)
                
                # Get all product links
                product_cards = page.locator('.i-card')
                count = product_cards.count()
                print(f"Найдено товаров на странице: {count}")
                
                product_links = []
                for i in range(count):
                    if len(product_links) >= config.PRODUCTS_PER_CATEGORY:
                        break
                    
                    card = product_cards.nth(i)
                    link_elem = card.locator('.i-card-name a').first
                    if link_elem.count() > 0:
                        href = link_elem.get_attribute('href')
                        if href:
                            if not href.startswith('http'):
                                href = config.SOURCE_URL + href
                            product_links.append(href)
                
                print(f"Отобрано для парсинга: {len(product_links)}")

                # Visit each product page
                collected_from_category = 0
                for product_url in product_links:
                    if collected_from_category >= config.PRODUCTS_PER_CATEGORY:
                        break

                    try:
                        print(f"  [{collected_from_category + 1}/](#:~:text=,PRODUCTS_PER_CATEGORY]%20%D0%9F%D0%B0%D1%80%D1%81%D0%B8%D0%BD%D0%B3%3A%20%7Bproduct_url%7D...", end=" ")
                        page.goto(product_url, wait_until="domcontentloaded", timeout=60000)
                        
                        # Extract Details
                        title = page.locator('h1').first.inner_text().strip()
                        
                        price_elem = page.locator('.catalog-element-price-value').first
                        price = "0"
                        if price_elem.count() > 0:
                            price = self.clean_price(price_elem.inner_text())
                            
                        description = ""
                        desc_elem = page.locator('.catalog-element-card-description')
                        if desc_elem.count() > 0:
                            description = desc_elem.inner_text().strip()
                        
                        properties = {}
                        props = page.locator('.catalog-element-property').all()
                        for prop in props:
                            name = prop.locator('.catalog-element-property-name').inner_text().strip()
                            val = prop.locator('.catalog-element-property-value').inner_text().strip()
                            properties[name] = val
                            
                        full_description = description
                        if properties:
                            full_description += "\n\nХарактеристики:\n" + "\n".join([f"{k}: {v}" for k, v in properties.items()])

                        # Images
                        images = []
                        slides = page.locator('.f-carousel__slide img').all()
                        for img in slides:
                            src = img.get_attribute('data-original') or img.get_attribute('src')
                            if src:
                                if not src.startswith('http'):
                                    src = config.SOURCE_URL + src
                                if src not in images:
                                    images.append(src)
                        
                        main_image = images[0] if images else ""
                        
                        # Quantity
                        quantity = 0
                        qty_elems = page.locator('.catalog-element-quantity').all()
                        for qty_el in qty_elems:
                            txt = qty_el.inner_text()
                            match = re.search(r'(\d+)', txt)
                            if match:
                                quantity += int(match.group(1))
                        
                        if quantity == 0:
                            quantity = 100
                            
                        # Translations (4 languages)
                        print("переводы...", end=" ")
                        title_en = self.translate_text(title, 'en')
                        title_uz = self.translate_text(title, 'uz')
                        title_uz_cyr = self.translate_text(title, 'uz-cyr')
                        
                        desc_en = self.translate_text(full_description, 'en')
                        desc_uz = self.translate_text(full_description, 'uz')
                        desc_uz_cyr = self.translate_text(full_description, 'uz-cyr')
                        
                        # Construct Product Object
                        product_data = {
                            'title': title,
                            'title_en': title_en,
                            'title_uz': title_uz,
                            'title_uz_cyr': title_uz_cyr,
                            
                            'description': full_description,
                            'description_en': desc_en,
                            'description_uz': desc_uz,
                            'description_uz_cyr': desc_uz_cyr,
                            
                            'price': price,
                            'quantity': quantity,
                            'image_url': main_image,
                            'images': images,
                            'product_url': product_url,
                            'gender': gender,
                            'category': category_name,
                            'parent_category': parent_category,
                        }
                        
                        self.products.append(product_data)
                        collected_from_category += 1
                        total_collected += 1
                        print(f"✅ ({quantity} шт)")
                        
                    except Exception as e:
                        print(f"❌ Ошибка: {e}")
                
                print(f"✅ Собрано из категории '{category_name}': {collected_from_category}")
            
            browser.close()
            print(f"\n{'='*60}")
            print(f"Итого собрано ({parent_category}): {total_collected}")
            print(f"{'='*60}")
        
        return total_collected
    
    def download_images(self):
        print("\nЗагрузка изображений...")
        Path(config.IMAGES_DIR).mkdir(parents=True, exist_ok=True)
        
        for i, product in enumerate(self.products):
            product['local_images'] = []
            
            original_images = product.get('images', [])
            if not original_images and product.get('image_url'):
                original_images = [product['image_url']]
            
            for j, img_url in enumerate(original_images):
                if not img_url:
                    continue
                    
                try:
                    response = requests.get(img_url, timeout=10)
                    if response.status_code == 200:
                        ext = img_url.split('.')[-1].split('?')[0]
                        if ext not in ['jpg', 'jpeg', 'png', 'webp']:
                            ext = 'jpg'
                        
                        filename = f"product_{i+1}_{j+1}.{ext}"
                        filepath = os.path.join(config.IMAGES_DIR, filename)
                        
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        
                        product['local_images'].append(filepath)
                        
                        # Set main image for compatibility
                        if j == 0:
                            product['local_image'] = filepath
                            
                        print(f"  [{i+1}/{len(self.products)}] Загружено: {filename}")
                        
                except Exception as e:
                    print(f"  Ошибка загрузки изображения {img_url}: {e}")
            
            # Fallback if no images downloaded
            if 'local_image' not in product:
                product['local_image'] = None
    
    def save_to_json(self):
        Path(config.DATA_DIR).mkdir(parents=True, exist_ok=True)
        
        with open(config.PRODUCTS_JSON, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, ensure_ascii=False, indent=2)
        
        print(f"\nДанные сохранены в {config.PRODUCTS_JSON}")
        print(f"Всего товаров: {len(self.products)}")


def main():
    scraper = TerraProScraper()
    
    scraper.scrape_products(config.MEN_CATEGORIES, "Мужчины", "мужской")
    scraper.scrape_products(config.WOMEN_CATEGORIES, "Женщины", "женский")
    
    scraper.download_images()
    scraper.save_to_json()
    
    print("\n✅ Парсинг завершен!")


if __name__ == "__main__":
    main()
