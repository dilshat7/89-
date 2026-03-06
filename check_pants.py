import json, os

data = json.load(open(r"C:\Users\ddjab\product-transfer\data\products.json", encoding="utf-8"))
print(f"{'№':<4} {'Кол-во файлов':<15} {'Пример пути'}")
print("-" * 70)
for i, p in enumerate(data, 1):
    imgs = p.get("local_images", [])
    existing = [f for f in imgs if os.path.exists(f)]
    print(f"#{i:<3} {len(existing):<15} {existing[0] if existing else 'НЕТ ФАЙЛОВ'}")
