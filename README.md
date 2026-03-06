# Инструкция по запуску

## Шаг 1: Установка Playwright

```powershell
cd c:\Users\ddjab\product-transfer
pip install -r requirements.txt
playwright install
```

## Шаг 2: Парсинг товаров с terrapro.uz

```powershell
python scraper.py
```

**Результат:** Будет создана папка `data/` с файлом `products.json` и папка `data/images/` с изображениями.

## Шаг 3: Загрузка товаров на aichat.ikujo.com

```powershell
python uploader.py
```

**Что произойдет:**
1. Авторизация на aichat.ikujo.com
2. Создание категорий (если не существуют)
3. Загрузка товаров с изображениями
4. Вывод статистики (успешно/ошибки)

## Тестовый запуск (5 товаров)

Для теста измените в `uploader.py` строку:
```python
limit=5  # вместо 100
```

## Полная загрузка (100 товаров)

Измените в `uploader.py`:
```python
limit=100  # или None для всех
```
