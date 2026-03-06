import requests

BASE_URL   = "https://aichat.ikujo.com"
EMAIL      = "sale.fix@hotmail.com"
PASSWORD   = "Password1!"
ACCOUNT_ID = 71

DELETE_CATEGORY_RU = "Мужские аксессуары"

session = requests.Session()
session.headers.update({"Content-Type": "application/json"})

resp = session.post(f"{BASE_URL}/auth/sign_in", json={"email": EMAIL, "password": PASSWORD})
resp.raise_for_status()
if "access-token" in resp.headers:
    session.headers.update({
        "access-token": resp.headers["access-token"],
        "client":       resp.headers["client"],
        "uid":          resp.headers["uid"],
    })
    del session.headers["Content-Type"]
print("✅ Авторизован")

# Найти категорию
r = session.get(f"{BASE_URL}/api/v1/accounts/{ACCOUNT_ID}/product_categories", params={"per_page": 200})
cats = r.json()
cats = cats if isinstance(cats, list) else cats.get("data", [])

target_id = None
for cat in cats:
    name_obj = cat.get("name", {})
    name_ru = (name_obj.get("ru") or name_obj.get("en") or "").strip() if isinstance(name_obj, dict) else str(name_obj).strip()
    if name_ru == DELETE_CATEGORY_RU:
        target_id = cat["id"]
        print(f"Найдена категория '{DELETE_CATEGORY_RU}' (ID={target_id})")
        break

if not target_id:
    print(f"❌ Категория '{DELETE_CATEGORY_RU}' не найдена!")
    exit(1)

# Удалить товары этой категории
page = 1
deleted_products = 0
while True:
    r = session.get(f"{BASE_URL}/api/v1/accounts/{ACCOUNT_ID}/products",
                    params={"page": page, "per_page": 50})
    r.raise_for_status()
    data = r.json()
    items = data if isinstance(data, list) else data.get("data", data.get("products", []))
    if not items:
        break
    for item in items:
        if item.get("product_category_id") == target_id:
            pid = item["id"]
            dr = session.delete(f"{BASE_URL}/api/v1/accounts/{ACCOUNT_ID}/products/{pid}")
            if dr.status_code in (200, 204):
                print(f"  🗑️  Товар ID={pid} удалён")
                deleted_products += 1
    if len(items) < 50:
        break
    page += 1

print(f"Товаров удалено: {deleted_products}")

# Удалить саму категорию
dr = session.delete(f"{BASE_URL}/api/v1/accounts/{ACCOUNT_ID}/product_categories/{target_id}")
if dr.status_code in (200, 204):
    print(f"✅ Категория '{DELETE_CATEGORY_RU}' (ID={target_id}) удалена")
else:
    print(f"❌ Ошибка удаления категории: {dr.status_code}: {dr.text[:100]}")
