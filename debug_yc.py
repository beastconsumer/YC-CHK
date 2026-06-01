"""Find Turnstile in YC - deep search"""
import time, re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--window-size=1366,768")
options.add_argument("--headless=new")  
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)
driver.get("https://account.ycombinator.com/?continue=https%3A%2F%2Fwww.startupschool.org%2Fusers%2Fsign_in")
time.sleep(5)

ps = driver.page_source

# Search for ANY turnstile-related content
for line in ps.split('\n'):
    if 'turnstile' in line.lower() or 'cf-' in line.lower() or 'challenge' in line.lower():
        print(line[:200])

# Check for Cloudflare Turnstile script
scripts = driver.find_elements("tag name", "script")
for s in scripts:
    src = s.get_attribute("src") or ""
    if "turnstile" in src.lower() or "challenge" in src.lower():
        print(f"SCRIPT: {src}")

# Check all iframes  
iframes = driver.find_elements("tag name", "iframe")
for f in iframes:
    src = f.get_attribute("src") or ""
    print(f"IFRAME: {src[:200]}")

# Find any data-sitekey or similar
for el in driver.find_elements("css selector", "[data-sitekey]"):
    print(f"SITEKEY: {el.get_attribute('data-sitekey')}")
for el in driver.find_elements("css selector", "[data-turnstile]"):
    print(f"TURNSTILE: {el.get_attribute('data-turnstile')}")

driver.quit()
