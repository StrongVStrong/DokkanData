from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import json

# Selenium setup
driver = webdriver.Chrome()  # Ensure ChromeDriver is installed and in PATH

# Data storage
character_data = []
character_links = []
test_links = [
    "https://dokkan.wiki/cards/1026901",
    "https://dokkan.wiki/cards/1014761"
]

# Predefined arrays for valid links and categories
valid_links = {}

with open("dokkan_links.json", "r", encoding="utf-8") as f:
    valid_links = json.load(f)


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

        # Extract Links
        try:
            # Locate the parent container for links
            links_container = driver.find_element(By.CLASS_NAME, "row.g-2.justify-content-center.align-items-center")
            
            # Find all `div` elements with class `col-auto` within the container
            link_elements = links_container.find_elements(By.CLASS_NAME, "col-auto")
            
            # Extract the text from nested `div.text` inside each link element
            link_names = [link.find_element(By.CLASS_NAME, "text").text.strip() for link in link_elements]
            
            print(f"Extracted Links: {link_names}")
        except Exception as e:
            print(f"Error extracting links: ")

        # Extract Categories
        try:
            # Locate the container with id="categories"
            categories_section = driver.find_element(By.ID, "categories")
            
            # Within this section, find the specific row containing categories
            categories_container = categories_section.find_element(By.CLASS_NAME, "row.g-2.justify-content-center.align-items-center")
            
            # Find all category elements (div.col-auto)
            category_elements = categories_container.find_elements(By.CLASS_NAME, "col-auto")
            
            # Extract `alt` or `title` attributes from `img` tags inside each `col-auto`
            category_names = [
                cat.find_element(By.TAG_NAME, "img").get_attribute("alt") or 
                cat.find_element(By.TAG_NAME, "img").get_attribute("title")
                for cat in category_elements
            ]
            
            print(f"Extracted Categories: {category_names}")
        except Exception as e:
            print(f"Error extracting categories: ")


        # Extract Transformation Condition
        transformation_condition = []
        try:
            # Locate the container with id="transformations"
            transformations_section = driver.find_element(By.ID, "transformations")
            
            # Find the first paragraph element with class "mb-0" containing the transformation condition text
            transformation_condition = transformations_section.find_element(By.CLASS_NAME, "mb-0").text.strip()
            
            print(f"Extracted Transformation Condition: {transformation_condition}")
        except Exception as e:
            print(f"Error extracting transformation condition: ")


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

        
# Function to determine the total number of pages dynamically
def get_total_pages():
    try:
        # Navigate to the first page
        driver.get(base_url.format(1))
        
        # Wait for the pagination section to load
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.CLASS_NAME, "pagination"))
        )
        
        # Locate the pagination element
        pagination = driver.find_element(By.CLASS_NAME, "pagination")
        
        # Get all page numbers within the pagination
        page_numbers = pagination.find_elements(By.CLASS_NAME, "page-link")
        
        # Extract the maximum page number from the list
        max_page = max([int(page.text) for page in page_numbers if page.text.isdigit()])
        return max_page
    except Exception as e:
        print(f"Error determining the total number of pages: {e}")
        return 1  # Default to 1 if unable to fetch the total page count


# Base URL for pagination
base_url = "https://dokkan.wiki/cards#!(p:{})"
# Set to track processed pages
processed_pages = set()

try:
    # Get the total number of pages dynamically
    total_pages = get_total_pages()
    print(f"Total pages found: {total_pages}")

    for page in range(1, 2):  # Use the dynamic total page count
        if page in processed_pages:
            print(f"Skipping already processed page {page}.")
            continue  # Skip already processed pages

        url = base_url.format(page)
        print(f"Scraping page {page}: {url}")  # Log current page

        # Navigate to the page and refresh to ensure proper loading
        driver.get(url)
        driver.refresh()

        # Wait for the card elements to load
        WebDriverWait(driver, 1).until(
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
                print(f"Found character: {link}")  # Log unique links

        # If fewer cards are found, print a note (optional for debugging)
        if len(cards) < 32:
            print(f"Note: Page {page} has fewer than 32 cards. Processing all found cards.")

        print(f"Completed page {page}. Moving to the next page.")
        processed_pages.add(page)  # Mark page as processed

    print(f"Collected {len(character_links)} unique character links.")

    # Step 2: Visit Each Character Page
    total_characters = len(character_links)
    for current_index, link in enumerate(character_links, start = 1):
        print(f"\nProcessing character {current_index}/{total_characters}: {link}")
        driver.get(link)

        # Wait for the page to load by ensuring a key element is present
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )

        # Extract Base Data
        extract_character_data("Base")
        
        #Save data
        df = pd.DataFrame(character_data)
        df.to_csv("dokkan_character_details_test.csv", index=False)

        # Switch to EZA Tab if Available
        try:
            eza_tab = WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "btn.dokkan-btn-tab.p-3.right"))
            )
            eza_tab.click()

            # Wait for the EZA tab content to load
            WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.CLASS_NAME, "some-class-inside-eza-tab"))
            )
            extract_character_data("EZA")
        except Exception as e:
            print(f"EZA tab not found for {link}. Checking for Base tab: ")
            try:
                base_tab = WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "btn.dokkan-btn-tab.p-3.left"))
                )
                base_tab.click()

                # Wait for the Base tab content to load
                WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "some-class-inside-base-tab"))
                )
                extract_character_data("Base")
            except Exception as e:
                print(f"Base tab not found for {link}: ")

        # Handle Transformations
        try:
            # Locate the transformations section by its ID
            transformations_section = driver.find_element(By.ID, "transformations")
            
            # Locate all transformation containers (list-group-item blocks)
            transformation_items = transformations_section.find_elements(By.CLASS_NAME, "list-group-item")
            
            total_transformations = len(transformation_items)
            print(f"Found {total_transformations} transformations for this character.")

            # Process transformations one by one
            for i, item in enumerate(transformation_items):
                # Re-locate transformations section and items after each navigation
                transformations_section = driver.find_element(By.ID, "transformations")
                transformation_items = transformations_section.find_elements(By.CLASS_NAME, "list-group-item")
                
                # Get the current transformation link
                transformation_link_element = transformation_items[i].find_element(By.CLASS_NAME, "card-thumb-wrapper")
                transformation_link = transformation_link_element.get_attribute("href")

                # Get the transformation condition for the *next* transformation (offset by one index)
                transformation_condition = "N/A"
                if i < total_transformations - 1:  # Skip condition extraction for the last transformation
                    try:
                        next_condition_element = transformation_items[i + 1].find_element(By.CLASS_NAME, "mb-0")
                        transformation_condition = next_condition_element.text.strip()
                        print(f"Extracted Transformation Condition for Transformation {i + 1}: {transformation_condition}")
                    except Exception as e:
                        print(f"Error extracting transformation condition for Transformation {i + 1}: ")

                # Navigate to the transformation page
                if transformation_link and transformation_link != driver.current_url:
                    print(f"Processing Transformation {i + 1}/{total_transformations}: {transformation_link}")
                    driver.get(transformation_link)
                    
                    # Wait for the transformation page to load
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "h1"))
                    )
                    
                    # Extract data for this transformation
                    extract_character_data("Transformation")

                    # Update the "Transformation Condition" field with the offset condition
                    character_data[-1]["Transformation Condition"] = transformation_condition

        except Exception as e:
            print(f"No transformations found or error occurred: ")





except KeyboardInterrupt:
    print("Force stop detected. Saving progress...")
except Exception as e:
    print(f"Error during scraping: {e}")


# Quit the Driver
driver.quit()

