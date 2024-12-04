import pandas as pd
import re

# Read the existing CSV file into a DataFrame
df = pd.read_csv('processed_data.csv')  # Replace with the path to your actual CSV file

# Function to extract stats
def extract_stats(stats_str):
    # Regular expression to extract the values for HP, ATK, and DEF
    pattern = r"HP (\d{1,3},\d{1,3}) (\d{1,3},\d{1,3}) \| ATK (\d{1,3},\d{1,3}) (\d{1,3},\d{1,3}) \| DEF (\d{1,3},\d{1,3}) (\d{1,3},\d{1,3})"
    match = re.match(pattern, stats_str)

    if match:
        # Return the values as a tuple
        return match.groups()
    return None

# Apply the function to the Stats column
df[['HP 55%', 'HP 100%', 'ATK 55%', 'ATK 100%', 'DEF 55%', 'DEF 100%']] = df['Stats 55% 100%'].apply(lambda x: pd.Series(extract_stats(x)))

# Drop the original Stats column if no longer needed
df = df.drop(columns=['Stats 55% 100%'])

# Save the updated DataFrame to a new CSV file
df.to_csv('updated_stats.csv', index=False)  # This will create a new CSV file with the updated data

# Display the updated DataFrame to the user (optional)
import ace_tools as tools; tools.display_dataframe_to_user(name="Updated Stats DataFrame", dataframe=df)

# Optional: Check if everything looks correct
print(df)
