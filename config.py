SOURCE_URL = "https://terrapro.uz"
TARGET_URL = "https://aichat.ikujo.com"

TARGET_EMAIL = "sale.fix@hotmail.com"
TARGET_PASSWORD = "Password1!"

MEN_CATEGORIES = {
    "Верхняя одежда": "https://terrapro.uz/catalog/verkhnyaya-odezhda/",
    "Рубашки": "https://terrapro.uz/catalog/rubashki/",
    "Аксессуары": "https://terrapro.uz/catalog/aksessuary/",
    "Брюки": "https://terrapro.uz/catalog/kategoriya-bryuki/",
    "Шорты": "https://terrapro.uz/catalog/kategoriya-shorty/",
}

WOMEN_CATEGORIES = {
    "Верхняя одежда": "https://terrapro.uz/woman/catalog/verkhnyaya-odezhda_1/",
    "Пиджаки и жакеты": "https://terrapro.uz/woman/catalog/pidzhaki-i-zhakety/",
    "Юбки": "https://terrapro.uz/woman/catalog/yubki/",
    "Блузки и рубашки": "https://terrapro.uz/woman/catalog/bluzki-i-rubashki/",
    "Брюки": "https://terrapro.uz/woman/catalog/bryuki_2/",
}

PRODUCTS_PER_CATEGORY = 10

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
PRODUCTS_JSON = os.path.join(DATA_DIR, "products.json")
