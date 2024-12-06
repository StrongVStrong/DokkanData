import pandas as pd
import spacy

# Load SpaCy's English model
nlp = spacy.load("en_core_web_sm")

# List of keywords to stop at (like ATK, DEF, Guards, etc.)
stop_keywords = ['ATK', 'DEF', 'Guards', 'Activates', 'when', 'and']

# Read the existing CSV file into a DataFrame
df = pd.read_csv('truefinaldata.csv')  # Replace 'your_file.csv' with your file path

# Function to extract passive name and skill description
def extract_passive_name_and_skill(description):
    # Ensure the description is a valid string and not NaN
    if pd.notna(description) and isinstance(description, str) and description.strip():
        # Process the description using SpaCy
        doc = nlp(description)
        
        # Extract nouns and find the last noun before any stop keyword
        nouns = []
        passive_name = None
        for token in doc:
            # Check if the token is a noun or proper noun and not in stop keywords
            if token.pos_ in ['NOUN', 'PROPN']:
                if not any(keyword in token.text for keyword in stop_keywords):
                    nouns.append(token.text)
                else:
                    break  # Stop if a keyword is encountered
        
        # If we found nouns, the last one is considered the passive name
        if nouns:
            passive_name = " ".join(nouns)
            skill_description = description[len(" ".join(nouns)):].strip()
        else:
            passive_name = None
            skill_description = description.strip()

        return passive_name, skill_description
    return None, None  # Return None if description is invalid

# Apply the function to the 'Passive Skill' column and create 'Passive Name' and 'Passive Skill' columns
df[['Passive Name', 'Passive Skill']] = df['Passive Skill'].apply(lambda x: pd.Series(extract_passive_name_and_skill(x)))

# Reorder columns to place 'Passive Name' right before 'Passive Skill'
cols = ['State', 'Name', 'Subname', 'Stats 55% 100%', 'HP 55%', 'HP 100%', 'ATK 55%', 'ATK 100%', 
        'DEF 55%', 'DEF 100%', 'Leader Skill', 'Passive Name', 'Passive Skill', 'Active Skill', 
        'Super Attack (12 Ki) Effect', 'Super Attack (18 Ki) Effect', 'Links', 'Categories', 
        'Transformation Condition', 'Release Date', 'Ki Multiplier', 'DMG Multiplier']
df = df[cols]

# Save the updated DataFrame to a new CSV file
df.to_csv('updated_file.csv', index=False)  # Replace 'updated_file.csv' with your desired output file name

print("Updated CSV with Passive Name and Passive Skill saved as 'updated_file.csv'")
