import os
from PIL import Image

IMAGES_DIR = 'data/images'
MAX_SIZE = (1024, 1024)
QUALITY = 80

def optimize_images():
    if not os.path.exists(IMAGES_DIR):
        print(f"Папка {IMAGES_DIR} не найдена.")
        return

    files = [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    total = len(files)
    
    print(f"Найдено {total} изображений для оптимизации in {IMAGES_DIR}...")
    
    optimized_count = 0
    saved_space = 0
    
    for i, filename in enumerate(files, 1):
        filepath = os.path.join(IMAGES_DIR, filename)
        
        try:
            original_size = os.path.getsize(filepath)
            
            with Image.open(filepath) as img:
                # Convert to RGB (remove alpha channel if PNG)
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Resize if larger than max
                if img.width > MAX_SIZE[0] or img.height > MAX_SIZE[1]:
                    img.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)
                
                # Save back as optimized JPEG
                # We overwrite the file or save as .jpg if it was .png/.webp
                new_filepath = os.path.splitext(filepath)[0] + '.jpg'
                
                img.save(new_filepath, 'JPEG', quality=QUALITY, optimize=True)
                
                new_size = os.path.getsize(new_filepath)
                saved = original_size - new_size
                
                # Remove original if extension changed
                if new_filepath != filepath:
                    os.remove(filepath)
                
                print(f"[{i}/{total}] {filename}: {original_size/1024:.1f}KB -> {new_size/1024:.1f}KB (Saved {saved/1024:.1f}KB)")
                saved_space += saved
                optimized_count += 1
                
        except Exception as e:
            print(f"❌ Ошибка с {filename}: {e}")

    print(f"\n✅ Завершено!")
    print(f"   Оптимизировано: {optimized_count}")
    print(f"   Сэкономлено места: {saved_space / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    try:
        from PIL import Image
    except ImportError:
        print("❌ Библиотека Pillow не установлена.")
        print("   Установите: pip install Pillow")
        exit(1)
        
    optimize_images()
