import json, os, shutil, glob
from PIL import Image

SRC_JSON = r"C:\Users\ddjab\OneDrive\Рабочий стол\product-transfer\data\products.json"
DST_DIR = r"C:\Users\ddjab\OneDrive\Рабочий стол\Выгрузка товар"
DST_IMAGES = os.path.join(DST_DIR, "images")

MAX_PHOTOS = 5

for f in glob.glob(os.path.join(DST_IMAGES, "*.jpg")):
    os.remove(f)
print("Старые фото удалены")

data = json.load(open(SRC_JSON, encoding="utf-8"))
print(f"Загружено {len(data)} товаров")

result = []
for i, p in enumerate(data, 1):
    new_images = []
    local_imgs = p.get("local_images", [])
    if not local_imgs and p.get("local_image"):
        local_imgs = [p["local_image"]]

    for j, img_path in enumerate(local_imgs[:MAX_PHOTOS], 1):
        if not os.path.exists(img_path):
            continue
        jpg_name = f"product_{i}_{j}.jpg"
        jpg_path = os.path.join(DST_IMAGES, jpg_name)
        ext = os.path.splitext(img_path)[1].lower()
        if ext in (".jpg", ".jpeg"):
            shutil.copy2(img_path, jpg_path)
        else:
            img = Image.open(img_path).convert("RGB")
            img.save(jpg_path, "JPEG", quality=90)
        new_images.append(jpg_path)

    product = {
        "title": p.get("title", ""),
        "title_en": p.get("title_en", ""),
        "description": p.get("description", ""),
        "description_en": p.get("description_en", ""),
        "price": p.get("price", ""),
        "quantity": p.get("quantity", 1),
        "gender": p.get("gender", ""),
        "category": p.get("category", ""),
        "parent_category": p.get("parent_category", ""),
        "images": new_images,
        "image_url": p.get("image_url", ""),
    }
    result.append(product)
    if i % 10 == 0:
        print(f"  {i}/100 обработано")

dst_json = os.path.join(DST_DIR, "products.json")
json.dump(result, open(dst_json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

total_photos = sum(len(p["images"]) for p in result)
print(f"Готово! {len(result)} товаров, {total_photos} JPG (макс {MAX_PHOTOS} на товар)")

import openpyxl

wb = openpyxl.Workbook()

ws1 = wb.active
ws1.title = "Названия"
ws1.append(["№", "Категория", "Подкатегория", "title (RU)", "title_en (EN)", "title_uz (перевод)", "title_uz_cyr (перевод)"])
for i, p in enumerate(result, 1):
    ws1.append([i, p["parent_category"], p["category"], p["title"], p["title_en"], "", ""])

ws2 = wb.create_sheet("Описания")
ws2.append(["№", "Категория", "Подкатегория", "description (RU)", "description_en (EN)", "description_uz (перевод)", "description_uz_cyr (перевод)"])
for i, p in enumerate(result, 1):
    ws2.append([i, p["parent_category"], p["category"], p["description"], p["description_en"], "", ""])

for ws in [ws1, ws2]:
    for col in ws.columns:
        max_len = max(len(str(cell.value or "")[:60]) for cell in col)
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 60)

out_xlsx = os.path.join(DST_DIR, "translations.xlsx")
wb.save(out_xlsx)
print(f"Excel: {out_xlsx}")
