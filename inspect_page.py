from playwright.sync_api import sync_playwright
import time

def inspect():
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        url = "https://terrapro.uz/catalog/kurtka_1/"
        print(f"Going to {url}...")
        # Используем domcontentloaded вместо networkidle - это надежнее
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)  # Wait for any dynamic content
        
        print("Saving screenshot...")
        page.screenshot(path="debug_screenshot.png")
        
        print("Saving HTML...")
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(page.content())
            
        print("Done! debug_screenshot.png and debug_page.html saved.")
        browser.close()

if __name__ == "__main__":
    inspect()
