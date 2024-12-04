from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import json

# Selenium setup
driver = webdriver.Chrome()  # Ensure ChromeDriver is installed and in PATH

# Load existing data to append the release date to it
existing_data = pd.read_csv("processed_data2.csv")

# Function to extract character release date
def extract_release_date(state):
    try:
        # Ensure the state is part of the character page URL
        character_url = f"https://dokkan.wiki/cards/{state}"
        driver.get(character_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )

        # Extract the release date
        release_date = "N/A"
        try:
            # Assuming the release date is in the last transformation/awakening item
            transformations_section = driver.find_element(By.ID, "transformations")
            transformation_items = transformations_section.find_elements(By.CLASS_NAME, "list-group-item")
            if transformation_items:
                last_transformation_item = transformation_items[-1]  # Get the bottom-most item
                # Find the release date in this item
                release_date_div = last_transformation_item.find_element(By.CLASS_NAME, "release-date")  # Adjust class if needed
                release_date = release_date_div.text.strip() if release_date_div else "N/A"
        except Exception as e:
            print(f"Error extracting release date for {state}: {e}")
        
        # Append the release date to the existing character data
        existing_data.loc[existing_data['State'] == state, 'Release Date'] = release_date
        print(f"Added Release Date for {state}: {release_date}")

    except Exception as e:
        print(f"Error navigating or extracting data for {state}: {e}")

        
# Predefined arrays for valid links and categories
valid_links = {}

# Load links from the JSON file
with open("dokkan_links.json", "r", encoding="utf-8") as f:
    valid_links = json.load(f)

# Extract the list of character IDs or states from valid_links
character_links = []
for page in valid_links:
    character_links.extend(valid_links[page])  # Flatten the list of character links

# Now we have all the character links to process
print(f"Total characters to process: {len(character_links)}")

# Set to track processed pages
processed_pages = set()

try:
    # Go through each character's link and extract the release date
    for state in character_links:
        if state in processed_pages:
            print(f"Skipping already processed character {state}.")
            continue  # Skip already processed characters

        print(f"Processing character {state}...")
        
        # Extract release date for the current character
        extract_release_date(state)
        
        processed_pages.add(state)

    # Save updated character data with the release date to a new CSV file
    new_filename = "dokkan_character_data_with_release_dates.csv"
    existing_data.to_csv(new_filename, index=False)
    print(f"Release dates added and data saved to {new_filename}")

finally:
    driver.quit()
