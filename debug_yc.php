"""YC Login - submit via JS form submit + proper headers"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--window-size=1366,768")
options.add_argument("--headless=new")  
options.add_argument("--no-sandbox")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])

driver = webdriver.Chrome(options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"})

driver.get("https://account.ycombinator.com/?continue=https%3A%2F%2Fwww.startupschool.org%2Fusers%2Fsign_in")
time.sleep(5)

# Fill form
driver.find_element(By.ID, "ycid-input").send_keys("anushasheguri")
driver.find_element(By.ID, "password-input").send_keys("2ht.5.tC7DXvSVu")
time.sleep(0.5)

# Submit via JS (triggers native form handler)
driver.execute_script("""
    var form = document.getElementById('sign-in-card');
    if (form) {
        // Trigger submit button click properly
        var btn = form.querySelector('button[type="submit"]');
        if (btn) btn.click();
    }
""")
time.sleep(8)

# Check result
url = driver.current_url
ps = driver.page_source

print(f"URL: {url}")
print(f"Size: {len(ps)}")
print(f"Has 'startupschool': {'startupschool' in ps.lower()}")
print(f"Has 'sign_in': {'sign_in' in ps.lower()}")
print(f"Has 'error': {'error' in ps.lower()}")
print(f"Has 'validation': {'validation' in ps.lower()}")
print(f"Has 'dashboard': {'dashboard' in ps.lower()}")
print(f"Has 'welcome': {'welcome' in ps.lower()}")

# Check for any error messages
for el in driver.find_elements(By.CSS_SELECTOR, "[role='alert'], .error, .alert, .text-red-500, .text-red-600"):
    txt = el.text.strip()
    if txt: print(f"ERROR: {txt}")

# Take screenshot
driver.save_screenshot("yc_result.png")
print("\nScreenshot: yc_result.png")

driver.quit()
