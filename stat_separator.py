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

# Apply the function to the Stats column and create new columns for HP, ATK, DEF at 55% and 100%
new_columns = df['Stats 55% 100%'].apply(lambda x: pd.Series(extract_stats(x)))

# Name the new columns
new_columns.columns = ['HP 55%', 'HP 100%', 'ATK 55%', 'ATK 100%', 'DEF 55%', 'DEF 100%']

# Insert the new columns right after the original 'Stats 55% 100%' column
df = pd.concat([df.iloc[:, :df.columns.get_loc('Stats 55% 100%') + 1], new_columns, df.iloc[:, df.columns.get_loc('Stats 55% 100%') + 1:]], axis=1)

# Save the updated DataFrame to a new CSV file
df.to_csv('updated_stats.csv', index=False)  # This will create a new CSV file with the updated data

print("Updated CSV file saved as 'updated_stats.csv'")