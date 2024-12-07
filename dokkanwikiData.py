from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import json
import re
from selenium.common.exceptions import NoSuchElementException


# Selenium setup
driver = webdriver.Chrome()  # Ensure ChromeDriver is installed and in PATH

# Data storage
character_data = []
character_links = []
test_links = [
    "https://dokkan.wiki/cards/1007471",
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
        subname = driver.find_element(By.TAG_NAME, "h3").text.strip() if driver.find_elements(By.TAG_NAME, "h3") else None
        print("Character: ", name, subname)

        # Unit Stats
        stats_table = driver.find_elements(By.CLASS_NAME, "table-striped")
        unit_stats = [row.text.replace("\n", " ") for row in stats_table[0].find_elements(By.TAG_NAME, "tr")] if stats_table else [None]

        # Leader Skill
        leader_skill_elem = driver.find_element(By.ID, "leader-skill").text.replace("\n", " ").strip() if driver.find_elements(By.ID, "leader-skill") else None
        leader_skill = leader_skill_elem.replace("Leader Skill ", "").strip()
        # Remove the "(Extreme)" part for EZAs
        if "(Extreme)" in leader_skill:
            leader_skill = leader_skill.replace("(Extreme) ", "").strip()
        if "(Super Extreme)" in leader_skill:
            leader_skill = leader_skill.replace("(Super Extreme) ", "").strip()

        # Get Passive Name
        passive_name = None
        try:
            # Step 1: Find the first div inside #passive-skill div
            passive_skill_div = driver.find_element(By.ID, "passive-skill")

            first_div = passive_skill_div.find_element(By.XPATH, "div/div[1]")

            # Step 2: Extract all the text from this div
            div_text = first_div.text.strip()
            
            # Step 3: Get the second line (actual passive name)
            lines = div_text.split("\n")  # Split text by new lines
            if len(lines) > 1:
                passive_name = lines[1].strip()  # Get the second line
                print("Passive Skill:", passive_name)
            else:
                passive_name = None
                
        except Exception as e:
            print(f"An error occurred")

        # Get Passive Skills text
        passive_skill = None
        passive_skills_elements = driver.find_elements(By.XPATH, "//*[@id='passive-skill']/div/div[2]/ul/li")
        if not passive_skills_elements:
            print("No <li> elements found for Passive Skills.")
        passive_skill = ", ".join([element.text.strip() for element in passive_skills_elements]) if passive_skills_elements else None

        # Active Skill
        active_skill = driver.find_element(By.ID, "active-skill").text.replace("\n", " ").strip() if driver.find_elements(By.ID, "active-skill") else None

        # Super Attack Effects
        super_attack_12_effect = None
        super_attack_18_effect = None
        super_attack_12_name = None
        super_attack_18_name = None

        try:
            # 12 Ki Super Attack Name
            # Locate the div containing 'Super Attack (12 Ki)'
            super_attack_12_container = driver.find_element(
                By.XPATH, "//div[contains(@class, 'card-header') and contains(., 'Super Attack (12 Ki)')]/parent::div"
            )

            # Find the nested div with the class 'd-flex' within the container
            d_flex_div = super_attack_12_container.find_element(By.XPATH, ".//div[contains(@class, 'd-flex')]")

            # Extract all the text within the 'd-flex' div
            super_attack_12_text = d_flex_div.text.strip()
            
            # Split the text by newline and get the second line
            lines = super_attack_12_text.split("\n")
            super_attack_12_name = lines[1] if len(lines) > 1 else ""  # Get the second line if it exists
            
            #Strip EZA text
            if "(Extreme)" in super_attack_12_name:
                super_attack_12_name = super_attack_12_name.replace(" (Extreme)", "").strip()
            
            print(f"12 Ki: {super_attack_12_name}")
            
            # 12 Ki Super Attack Effect
            super_attack_12_effect = driver.find_element(
                By.XPATH, "//div[contains(@class, 'card-header') and contains(., 'Super Attack (12 Ki)')]/following-sibling::div[contains(@class, 'card-body')]/p[1]"
            ).text.strip()
        except Exception:
            print("Uh oh it broke")

        try:
            # 18 Ki Super Attack Name
            # Locate the div containing 'Super Attack (18 Ki)'
            super_attack_18_container = driver.find_element(
                By.XPATH, "//div[contains(@class, 'card-header') and contains(., 'Super Attack (18 Ki)')]/parent::div"
            )

            # Find the nested div with the class 'd-flex' within the container
            d_flex_div = super_attack_18_container.find_element(By.XPATH, ".//div[contains(@class, 'd-flex')]")

            # Extract all the text within the 'd-flex' div
            super_attack_18_text = d_flex_div.text.strip()
            
            # Split the text by newline and get the second line
            lines = super_attack_18_text.split("\n")
            super_attack_18_name = lines[1] if len(lines) > 1 else ""  # Get the second line if it exists
            
            #Strip EZA text
            if "(Extreme)" in super_attack_18_name:
                super_attack_18_name = super_attack_18_name.replace(" (Extreme)", "").strip()
            
            print(f"18 Ki: {super_attack_18_name}")
            
            # 18 Ki Super Attack Effect
            super_attack_18_effect = driver.find_element(
                By.XPATH, "//div[contains(@class, 'card-header') and contains(., 'Ultra Super Attack (18 Ki)')]/following-sibling::div[contains(@class, 'card-body')]/p[1]"
            ).text.strip()
        except Exception:
            print("")
            

        # Extract Links
        try:
            # Locate the parent container for links
            links_container = driver.find_element(By.CLASS_NAME, "row.g-2.justify-content-center.align-items-center")
            
            # Find all `div` elements with class `col-auto` within the container
            link_elements = links_container.find_elements(By.CLASS_NAME, "col-auto")
            
            # Extract the text from nested `div.text` inside each link element
            link_names = [link.find_element(By.CLASS_NAME, "text").text.strip() for link in link_elements]
            
        except Exception:
            print("")

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
        except Exception:
            print("")


        # Extract Transformation Condition
        transformation_condition = None
        try:
            # Locate the container with id="transformations"
            transformations_section = driver.find_element(By.ID, "transformations")
            
            # Find the first paragraph element with class "mb-0" containing the transformation condition text
            transformation_condition = transformations_section.find_element(By.CLASS_NAME, "mb-0").text.strip()
            
            print(f"Extracted Transformation Condition: {transformation_condition}")
        except Exception:
            print("")

        ki_multiplier = None
        try:
            
            # Try to find td[2] and td[1] at the same time, without waiting too long
            elements = driver.find_elements(By.XPATH, "//*[@id='stats']/div[2]/div[2]/table/tbody/tr[2]/td[2]") + \
                    driver.find_elements(By.XPATH, "//*[@id='stats']/div[2]/div[2]/table/tbody/tr[2]/td[1]")

            if elements:
                # Take the first found element
                element = elements[0]
                
                # Get the text from the located element
                text = element.text.strip()
                
                # Extract percentage (e.g., "150%" or "200%") using a regular expression
                match = re.search(r"(\d+%)", text)
                
                if match:
                    ki_multiplier = match.group(1)  # Extract only the percentage part
                else:
                    print("No percentage found in the text.")
            else:
                print("No relevant td found.")

        except Exception:
            print("")


        
        # Extract the most recent Release Date
        release_date = None
        try:
            # Wait for the release date section(s) to be visible
            # Use a more general XPath to capture all possible release date elements
            release_dates = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//*[@id='awakenings']/div[2]//div/p/span"))
            )
            
            # Retrieve the text of the last release date found (furthest down)
            if release_dates:
                release_date = release_dates[-1].text.strip()  # Take the last one (furthest down)
            else:
                print("No release dates found.")
        except Exception:
            print("")

        #Damage Multiplier
        dmg_multiplier = None
        # List of XPaths to check, starting with the most specific and falling back to the others
        xpath_list = [
            "//*[@id='app']/div[2]/div[2]/div[2]/div[4]/div[6]/div/div[2]/table/tbody/tr/td[5]",
            "//*[@id='app']/div[2]/div[2]/div[2]/div[4]/div[5]/div/div[2]/table/tbody/tr/td[4]",
            "//*[@id='app']/div[2]/div[2]/div[2]/div[4]/div[7]/div/div[2]/table/tbody/tr/td[4]",
            "//*[@id='app']/div[2]/div[2]/div[2]/div[4]/div[7]/div/div[2]/table/tbody/tr/td[3]",
            "//*[@id='app']/div[2]/div[2]/div[2]/div[4]/div[5]/div/div[2]/table/tbody/tr/td[3]",
            "//*[@id='app']/div[3]/div[2]/div[2]/div[4]/div[4]/div/div[2]/table/tbody/tr/td[3]",
            "//*[@id='app']/div[2]/div[2]/div[2]/div[4]/div[6]/div/div[2]/table/tbody/tr/td[3]",
            "//*[@id='app']/div[2]/div[2]/div[2]/div[4]/div[6]/div/div[2]/table/tbody/tr/td[3]",
            "//*[@id='app']/div[2]/div[2]/div[2]/div[4]/div[6]/div/div[2]/table/tbody/tr/td[4]"
        ]
        
        # Try to find the DMG Multiplier element using the list of XPaths
        i=0
        for xpath in xpath_list:
            print(f"Checking XPath: {i}")  # Debugging: print the current XPath being checked
            try:
                # Find the element using the XPath
                element = WebDriverWait(driver, 0.1).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                
                if element:
                    text = element.text.strip()
                    
                    # Extract the percentage (x%) using a regular expression
                    match = re.search(r"(\d+%)", text)
                    
                    if match:
                        dmg_multiplier = match.group(1)  # Extract only the percentage part
                        break  # Stop once we find the multiplier
                    else:
                        print("No percentage found in the DMG multiplier text.")
            except Exception:
                print(f"No element found for XPath: {i}. ")
                i += 1



        # Save the data for the state
        character_data.append({
            "State": state,
            "Name": name,
            "Subname": subname,
            "Stats 55% 100%": " | ".join(unit_stats),  # Flatten stats into a single string
            "Leader Skill": leader_skill,
            "Passive Name": passive_name,
            "Passive Skill": passive_skill,
            "Active Skill": active_skill,
            "Super Attack (12 Ki) Name": super_attack_12_name,
            "Super Attack (12 Ki) Effect": super_attack_12_effect,
            "Ultra Super Attack (18 Ki) Name": super_attack_18_name,
            "Ultra Super Attack (18 Ki) Effect": super_attack_18_effect,
            "Links": ", ".join(link_names),  # Only valid links are added
            "Categories": ", ".join(category_names),  # Only valid categories are added
            "Transformation Condition": transformation_condition,
            "Release Date": release_date,
            "Ki Multiplier": ki_multiplier,
            "DMG Multiplier": dmg_multiplier
        })

    except Exception:
        print(f"Error extracting character data process halted: ")

        
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
        print(f"Error determining the total number of pages: ")
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

        # If fewer cards are found, print a note
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
        df.to_csv("dokkan_character_details.csv", index=False)


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
                transformation_condition = None
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
                    WebDriverWait(driver, 1).until(
                        EC.presence_of_element_located((By.TAG_NAME, "h1"))
                    )
                    
                    # Extract data for this transformation
                    extract_character_data("Transformation")
                    
                    #Save data
                    df = pd.DataFrame(character_data)
                    df.to_csv("dokkan_character_details.csv", index=False)

                    # Update the "Transformation Condition" field with the offset condition
                    character_data[-1]["Transformation Condition"] = transformation_condition

        except Exception as e:
            print(f"No transformations for this character")





except KeyboardInterrupt:
    print("Force stop detected. Saving progress...")
except Exception as e:
    print(f"Error during scraping: ")


# Quit the Driver
driver.quit()