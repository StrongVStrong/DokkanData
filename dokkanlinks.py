from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import time

# Setup Selenium WebDriver with UI enabled
options = webdriver.ChromeOptions()
# Remove "--headless" to enable UI
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Base URL and page range
base_url = "https://dokkan.wiki/links/"
pages = range(1, 131)  # Page range from 1 to 130

# Dictionary to store results
link_data = {}

try:
    for page in pages:
        url = f"{base_url}{page}"
        print(f"Fetching: {url}")
        driver.get(url)
        time.sleep(2)  # Wait for the page to load fully
        
        # Extract the name (e.g., "Bombardment")
        try:
            name_element = driver.find_element(By.CSS_SELECTOR, "div.dokkan-link-wrapper div.text")
            name = name_element.text.strip()
            print(f"Page {page} Name: {name}")
        except Exception as e:
            print(f"Page {page}: Could not find name. Error: {e}")
            name = None

        # Extract Level 10 details (e.g., "Ki +2 and ATK & DEF +10%")
        try:
            level_elements = driver.find_elements(By.CSS_SELECTOR, "div.col-12.col-sm-6 div.text")
            if level_elements and len(level_elements) >= 10:
                level_10_details = level_elements[-1].text.strip()  # Get the last element (Level 10)
                print(f"Page {page} Level 10 Details: {level_10_details}")
            else:
                level_10_details = None
        except Exception as e:
            print(f"Page {page}: Could not find level 10 details. Error: {e}")
            level_10_details = None

        # Add to dictionary
        if name and level_10_details:
            link_data[name] = level_10_details
        else:
            print(f"Page {page}: Incomplete data (name: {name}, level 10: {level_10_details})")

finally:
    driver.quit()

# Save results to a JSON file
with open("dokkan_links.json", "w", encoding="utf-8") as f:
    json.dump(link_data, f, ensure_ascii=False, indent=4)

print("Data extraction complete! Results saved to dokkan_links.json.")
