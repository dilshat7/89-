from playwright.sync_api import sync_playwright
import time

def check_products():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("1. Переход на страницу логина...")
        page.goto("https://aichat.ikujo.com/app/login")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        print("2. Ввод учетных данных...")
        try:
            # Ждем появления формы
            page.wait_for_selector('input[placeholder="example@companyname.com"]', timeout=10000)
            
            # Заполняем email
            email_input = page.locator('input[placeholder="example@companyname.com"]')
            email_input.fill('d8638766@gmail.com')
            
            # Заполняем пароль
            password_input = page.locator('input[placeholder="Password"]')
            password_input.fill('Password1!')
        except Exception as e:
            print(f"   ❌ Не удалось найти поля ввода: {e}")
            print("   Создаю скриншот страницы логина...")
            page.screenshot(path="login_page_debug.png")
            print("   Скриншот: login_page_debug.png")
            browser.close()
            return
        
        print("3. Авторизация...")
        submit_button = page.locator('button:has-text("Login")')
        submit_button.click()
        
        print("4. Ожидание перехода...")
        time.sleep(5)
        
        print("5. Переход к товарам...")
        page.goto("https://aichat.ikujo.com/app/accounts/63/products/products")
        page.wait_for_load_state("networkidle")
        time.sleep(3)
        
        print("6. Создание скриншота...")
        page.screenshot(path="products_page.png", full_page=True)
        print("   ✅ Скриншот сохранен: products_page.png")
        
        print("\n✅ Браузер останется открытым на 15 секунд...")
        time.sleep(15)
        
        browser.close()
        print("Готово!")

if __name__ == "__main__":
    check_products()
