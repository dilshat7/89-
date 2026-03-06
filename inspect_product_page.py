from playwright.sync_api import sync_playwright
import time
import os

url = "https://terrapro.uz/catalog/kardigan/335167/?oid=336147&color=3e8928c7-9a12-11e9-bc84-e0b9a59b5726"

def run():
    print("Launching browser...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"Going to {url}...")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(5) # Wait for dynamic content
        
        # Save HTML
        print("Saving HTML...")
        html = page.content()
        with open("debug_product_page.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        print("Done! debug_product_page.html saved.")
        browser.close()

if __name__ == "__main__":
    run()
