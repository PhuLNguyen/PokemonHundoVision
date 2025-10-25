import requests
from bs4 import BeautifulSoup
import time
import random
import json
import sys

# 🚨 Required Selenium and Stealth imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium_stealth import stealth 

# ----------------- Configuration -----------------
START_ID = 1
END_ID = 1025 
OUTPUT_FILE = "pokemon_max_cp_data.json"

MAX_WAIT_TIME = 20    # Seconds to wait for elements to load
MAX_ATTEMPTS = 3      # Max times to try scraping a single Pokémon page
# -------------------------------------------------

all_pokemon_cp_data = []

# --- 1. FUNCTION TO INITIALIZE/RESTART DRIVER ---
def initialize_driver():
    """Initializes and returns a stable, stealth-enabled WebDriver instance."""
    
    # 🛡️ Configure Chrome Options for stability and stealth
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--log-level=3")             # Suppress console logging
    chrome_options.add_argument("--disable-dev-shm-usage")   # Essential for some environments (e.g., Docker)
    chrome_options.add_argument("window-size=1920x1080")     # Use a common resolution
    
    # Use a realistic and current User-Agent
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
    chrome_options.add_argument(f"user-agent={user_agent}") 
    
    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options) 
    driver.set_page_load_timeout(45) # Increased overall page load timeout
    
    # 🛡️ Apply stealth settings
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    return driver

# --- 2. INITIAL DRIVER SETUP ---
try:
    print("Initializing WebDriver...")
    driver = initialize_driver()
    print("WebDriver initialized successfully with stealth mode and custom options.")
except WebDriverException as e:
    print(f"\n❌ FATAL ERROR: Could not initialize WebDriver. Halting script.")
    print(e)
    sys.exit(1)

# --- 3. SCRAPING LOOP ---
print(f"Starting advanced scrape for Pokémon IDs {START_ID} to {END_ID}...")

for pokedex_id in range(START_ID, END_ID + 1):
    url = f"https://db.pokemongohub.net/pokemon/{pokedex_id}"
    
    attempts = 0
    
    # 💡 ATTEMPT LOOP: Tries up to MAX_ATTEMPTS to scrape the page
    while attempts < MAX_ATTEMPTS:
        attempts += 1
        
        try:
            # 3.1 Fetch the page content using the WebDriver
            driver.get(url)
            print(f"Fetching page for Pokémon #{pokedex_id} (Attempt {attempts})...")

            # 3.2 STATIC WAIT: Wait a random amount to ensure ALL dynamic content loads
            static_wait = random.uniform(2.0, 4.0)
            time.sleep(static_wait)

            # 3.3 Locate the Max CP Chart Table using explicit wait and XPath
            table_element = WebDriverWait(driver, MAX_WAIT_TIME).until(
                EC.presence_of_element_located((By.XPATH, "//h3[text()='Max CP Chart']/following-sibling::table[1]"))
            )
            
            # Extract data from the located table element
            table_html = table_element.get_attribute('outerHTML')
            table_soup = BeautifulSoup(table_html, 'html.parser')
            
            # --- Extraction Logic (No change needed here) ---
            pokemon_cp_entries = []
            page_soup = BeautifulSoup(driver.page_source, 'html.parser')
            pokemon_name_tag = page_soup.find('h1')
            pokemon_name = pokemon_name_tag.get_text(strip=True).split('(')[0].strip() if pokemon_name_tag else f"Unknown_Pokemon_{pokedex_id}"
            rows = table_soup.find_all('tr')[1:]

            for row in rows:
                cols = row.find_all('td')
                for i in range(0, len(cols), 2):
                    if i + 1 < len(cols):
                        level_text = cols[i].get_text(strip=True).replace('LVL', '')
                        cp_text = cols[i+1].get_text(strip=True).replace('CP', '').replace(',', '')
                        
                        try:
                            level = int(level_text)
                            cp = int(cp_text)
                            pokemon_cp_entries.append({'level': level, 'max_cp': cp})
                        except ValueError:
                            continue
            
            # Structure the final data object
            if pokemon_cp_entries:
                pokemon_record = {'_id': pokedex_id, 'name': pokemon_name, 'cp_data': pokemon_cp_entries}
                all_pokemon_cp_data.append(pokemon_record)
                print(f"✅ Successfully extracted data for {pokemon_name} (#{pokedex_id}).")
            else:
                print(f"⚠️ Found table, but extracted no CP entries for Pokémon #{pokedex_id}.")

            # If successful, exit the attempt loop
            break 

        except (TimeoutException, WebDriverException) as e:
            # 🛑 CRITICAL RECOVERY: Restart the WebDriver on failure 🛑
            print(f"🚨 Connection/Timeout Error: {type(e).__name__} during attempt {attempts}. Restarting driver...")
            
            # Quit the failed driver instance
            try:
                driver.quit()
            except:
                pass 
            
            # Initialize a new, fresh driver instance
            try:
                driver = initialize_driver()
            except Exception as e_restart:
                print(f"❌ Failed to restart driver: {e_restart}. Halting.")
                sys.exit(1)
            
            if attempts == MAX_ATTEMPTS:
                print(f"❌ Failed to scrape Pokémon #{pokedex_id} after {MAX_ATTEMPTS} attempts. Skipping.")
        
        except Exception as e:
             # General error handling
            print(f"⚠️ General error during scrape for Pokémon #{pokedex_id}: {e}")
            break


    # 4. 🐢 SLOW AND RANDOM DELAY (After successful scrape or final attempt failure)
    delay = random.uniform(3.0, 7.0)
    time.sleep(delay)
    print(f"Pausing for {delay:.2f} seconds...")
    
    # 5. Clear cookies periodically to avoid session tracking
    if pokedex_id % 100 == 0:
        driver.delete_all_cookies() 
        print(f"🔄 Cleared cookies at Pokémon #{pokedex_id} to reset session tracking.")


# --- Cleanup and Storage ---
print("\nScraping loop finished. Closing WebDriver...")
driver.quit() # 🛑 QUIT DRIVER AFTER LOOP 🛑

try:
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_pokemon_cp_data, f, indent=4, ensure_ascii=False)
    print(f"\n✅ Data for {len(all_pokemon_cp_data)} Pokémon saved to {OUTPUT_FILE}")
except Exception as e:
    print(f"\n❌ Error saving file: {e}")