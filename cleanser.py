import csv
import re
import pandas as pd

# Input and output file paths
input_file = "dokkan_character_details.csv"
output_file = "final_datax.csv"

# Step 1: Data Input & Initial Processing
with open(input_file, 'r') as infile:
    reader = csv.DictReader(infile)
    rows = list(reader)

# Step 2: Process and Clean Data
for row in rows:
    # Process Stats 55% and 100%
    stats = row["Stats 55% 100%"]
    stat_parts = stats.split('|')

    def get_values(stat_line):
        numbers = re.findall(r'\d[\d,]*', stat_line)
        if len(numbers) >= 4:
            return numbers[2], numbers[3]
        elif len(numbers) == 2:
            return numbers[1], numbers[1]
        else:
            return None, None

    hp_55, hp_100 = get_values(stat_parts[1]) if "HP" in stat_parts[1] else (None, None)
    atk_55, atk_100 = get_values(stat_parts[2]) if "ATK" in stat_parts[2] else (None, None)
    def_55, def_100 = get_values(stat_parts[3]) if "DEF" in stat_parts[3] else (None, None)
    
    row["Stats 55% 100%"] = f"HP {hp_55} {hp_100} | ATK {atk_55} {atk_100} | DEF {def_55} {def_100}"

# Step 3: Load Data into pandas DataFrame and Extract Stats
df = pd.DataFrame(rows)

def extract_stats(stats_str):
    pattern = r"HP (\d{1,3},\d{1,3}) (\d{1,3},\d{1,3}) \| ATK (\d{1,3},\d{1,3}) (\d{1,3},\d{1,3}) \| DEF (\d{1,3},\d{1,3}) (\d{1,3},\d{1,3})"
    match = re.match(pattern, stats_str)
    if match:
        return match.groups()
    return (None, None, None, None, None, None)

new_columns = df['Stats 55% 100%'].apply(lambda x: pd.Series(extract_stats(x)))
new_columns.columns = ['HP 55%', 'HP 100%', 'ATK 55%', 'ATK 100%', 'DEF 55%', 'DEF 100%']
df = pd.concat([df.iloc[:, :df.columns.get_loc('Stats 55% 100%') + 1], new_columns, df.iloc[:, df.columns.get_loc('Stats 55% 100%') + 1:]], axis=1)

# Step 4: Adjust Release Dates for Transformation Rows
last_base_release_date = None
for index, row in df.iterrows():
    if row['State'] == 'Base':
        last_base_release_date = row['Release Date']
    elif row['State'] == 'Transformation' and last_base_release_date is not None:
        df.at[index, 'Release Date'] = last_base_release_date

# Save the final DataFrame to the output file
df.to_csv(output_file, index=False)

print("Data has been processed and saved to 'final_datax.csv'")
