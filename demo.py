from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("Открываю aichat.ikujo.com...")
        page.goto("https://aichat.ikujo.com")
        
        print("Страница загружена. Браузер откроется на 10 секунд...")
        time.sleep(10)
        
        browser.close()
        print("Готово!")

if __name__ == "__main__":
    run()
