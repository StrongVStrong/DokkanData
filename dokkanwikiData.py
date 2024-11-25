from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Selenium setup
driver = webdriver.Chrome()  # Ensure ChromeDriver is installed and in PATH

# Data storage
character_data = []
character_links = []

# Predefined arrays for valid links and categories
valid_links = [
    "Saiyan Warrior Race", "Prepared for Battle", "Shocking Speed",
    "All in the Family", "Legendary Power", "Fierce Battle"
]
valid_categories = [
    "Pure Saiyans", "Fusion", "Joined Forces",
    "Movie Heroes", "Kamehameha", "Final Trump Card"
]

# Function to extract character data
def extract_character_data(state):
    try:
        # Unit Name and Subname
        name = driver.find_element(By.TAG_NAME, "h1").text.strip()
        subname = driver.find_element(By.TAG_NAME, "h3").text.strip() if driver.find_elements(By.TAG_NAME, "h3") else "N/A"

        # Unit Stats
        stats_table = driver.find_elements(By.CLASS_NAME, "table-striped")
        unit_stats = [row.text.replace("\n", " ") for row in stats_table[0].find_elements(By.TAG_NAME, "tr")] if stats_table else ["N/A"]

        # Leader Skill
        leader_skill = driver.find_element(By.ID, "leader-skill").text.replace("\n", " ").strip() if driver.find_elements(By.ID, "leader-skill") else "N/A"

        # Passive Skill
        passive_skill = driver.find_element(By.ID, "passive-skill").text.replace("\n", " ").strip() if driver.find_elements(By.ID, "passive-skill") else "N/A"

        # Active Skill
        active_skill = driver.find_element(By.ID, "active-skill").text.replace("\n", " ").strip() if driver.find_elements(By.ID, "active-skill") else "N/A"

        # Super Attack Effects
        super_attack_12_effect = "N/A"
        super_attack_18_effect = "N/A"

        try:
            # 12 Ki Super Attack Effect
            super_attack_12_effect = driver.find_element(
                By.XPATH, "//div[contains(@class, 'card-header') and contains(., 'Super Attack (12 Ki)')]/following-sibling::div[contains(@class, 'card-body')]/p[1]"
            ).text.strip()
        except Exception:
            super_attack_12_effect = "N/A"

        try:
            # 18 Ki Super Attack Effect
            super_attack_18_effect = driver.find_element(
                By.XPATH, "//div[contains(@class, 'card-header') and contains(., 'Ultra Super Attack (18 Ki)')]/following-sibling::div[contains(@class, 'card-body')]/p[1]"
            ).text.strip()
        except Exception:
            super_attack_18_effect = "N/A"

        # Links
        links_section = driver.find_elements(By.CLASS_NAME, "dokkan-link-wrapper")
        link_names = [
            link.text.strip() for link in links_section if link.text.strip() in valid_links
        ]

        # Categories
        categories_section = driver.find_elements(By.CLASS_NAME, "col-auto")
        category_names = [
            category.text.strip() for category in categories_section if category.text.strip() in valid_categories
        ]

        # Transformation Condition
        transformation_condition = driver.find_element(By.CLASS_NAME, "col-12.col-md.light").text.replace("\n", " ").strip() if driver.find_elements(By.CLASS_NAME, "col-12.col-md.light") else "N/A"

        # Save the data for the state
        character_data.append({
            "State": state,
            "Name": name,
            "Subname": subname,
            "Stats": " | ".join(unit_stats),  # Flatten stats into a single string
            "Leader Skill": leader_skill,
            "Passive Skill": passive_skill,
            "Active Skill": active_skill,
            "Super Attack (12 Ki) Effect": super_attack_12_effect,
            "Super Attack (18 Ki) Effect": super_attack_18_effect,
            "Links": ", ".join(link_names),  # Only valid links are added
            "Categories": ", ".join(category_names),  # Only valid categories are added
            "Transformation Condition": transformation_condition
        })

    except Exception as e:
        print(f"Error extracting character data for {state}: {e}")

        
# Base URL for pagination
base_url = "https://dokkan.wiki/cards#!(p:{})"
# Set to track processed pages
processed_pages = set()

try:
    for page in range(1, 3):  # Adjust range as needed
        if page in processed_pages:
            print(f"Skipping already processed page {page}.")
            continue  # Skip already processed pages

        url = base_url.format(page)
        print(f"Scraping page {page}: {url}")  # Log current page

        # Navigate to the page and refresh to ensure proper loading
        driver.get(url)
        driver.refresh()

        # Wait for the card elements to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "card-thumb-wrapper"))
        )

        # Collect character links
        cards = driver.find_elements(By.CLASS_NAME, "card-thumb-wrapper")
        print(f"Found {len(cards)} cards on page {page}.")  # Log card count

        # Loop through the cards and collect their links
        for card in cards[:32]:  # Process up to 32 cards on the page
            link = card.get_attribute('href')
            if link and link.startswith("https://dokkan.wiki/cards/") and link not in character_links:
                character_links.append(link)  # Add unique links
                print(f"Found character link: {link}")  # Log unique links

        # If fewer cards are found, print a note (optional for debugging)
        if len(cards) < 32:
            print(f"Note: Page {page} has fewer than 32 cards. Processing all found cards.")

        print(f"Completed page {page}. Moving to the next page.")
        processed_pages.add(page)  # Mark page as processed

    print(f"Collected {len(character_links)} unique character links.")

    # Step 2: Visit Each Character Page
    for link in character_links:
        driver.get(link)

        # Wait for the page to load by ensuring a key element is present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )

        # Extract Base Data
        extract_character_data("Base")

        # Switch to EZA Tab if Available
        try:
            eza_tab = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "btn.dokkan-btn-tab.p-3.right"))
            )
            eza_tab.click()

            # Wait for the EZA tab content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "some-class-inside-eza-tab"))
            )
            extract_character_data("EZA")
        except Exception as e:
            print(f"EZA tab not found for {link}. Checking for Base tab: {e}")
            try:
                base_tab = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "btn.dokkan-btn-tab.p-3.left"))
                )
                base_tab.click()

                # Wait for the Base tab content to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "some-class-inside-base-tab"))
                )
                extract_character_data("Base")
            except Exception as e:
                print(f"Base tab not found for {link}: {e}")

        # Handle Transformations
        try:
            transformations = driver.find_elements(By.CLASS_NAME, "card-thumb-wrapper")
            for transformation in transformations:
                transformation_link = transformation.get_attribute("href")
                if transformation_link and transformation_link != link:  # Avoid revisiting the main page
                    driver.get(transformation_link)

                    # Wait for the transformation page to load
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "h1"))
                    )
                    extract_character_data("Transformation")
        except Exception as e:
            print(f"No transformations found for {link}: {e}")

except KeyboardInterrupt:
    print("Force stop detected. Saving progress...")
except Exception as e:
    print(f"Error during scraping: {e}")



# Save Data to CSV
df = pd.DataFrame(character_data)
df.to_csv("dokkan_character_details_test.csv", index=False)
print("Data saved to dokkan_character_details_test.csv.")

# Quit the Driver
driver.quit()
