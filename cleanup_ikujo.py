import requests

BASE_URL   = "https://aichat.ikujo.com"
EMAIL      = "sale.fix@hotmail.com"
PASSWORD   = "Password1!"
ACCOUNT_ID = 71

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

# --- Удаляем товары ---
print("\nПолучаем товары...")
page = 1
deleted_products = 0
while True:
    r = session.get(f"{BASE_URL}/api/v1/accounts/{ACCOUNT_ID}/products", params={"page": page, "per_page": 50})
    r.raise_for_status()
    data = r.json()
    items = data if isinstance(data, list) else data.get("data", data.get("products", []))
    if not items:
        break
    for item in items:
        pid = item.get("id")
        dr = session.delete(f"{BASE_URL}/api/v1/accounts/{ACCOUNT_ID}/products/{pid}")
        if dr.status_code in (200, 204):
            print(f"  🗑️  Товар ID={pid} удалён")
            deleted_products += 1
        else:
            print(f"  ❌  Товар ID={pid} — ошибка {dr.status_code}")
    if len(items) < 50:
        break
    page += 1

print(f"\nИтого товаров удалено: {deleted_products}")

# --- Удаляем категории ---
print("\nПолучаем категории...")
r = session.get(f"{BASE_URL}/api/v1/accounts/{ACCOUNT_ID}/product_categories", params={"per_page": 200})
r.raise_for_status()
cats = r.json()
cats = cats if isinstance(cats, list) else cats.get("data", [])

deleted_cats = 0
for cat in cats:
    cid = cat.get("id")
    dr = session.delete(f"{BASE_URL}/api/v1/accounts/{ACCOUNT_ID}/product_categories/{cid}")
    if dr.status_code in (200, 204):
        print(f"  🗑️  Категория ID={cid} удалена")
        deleted_cats += 1
    else:
        print(f"  ❌  Категория ID={cid} — ошибка {dr.status_code}: {dr.text[:80]}")

print(f"\nИтого категорий удалено: {deleted_cats}")
print("\n✅ Платформа очищена!")
