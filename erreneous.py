import pandas as pd

# Read the existing CSV file into a DataFrame
df = pd.read_csv('updated_stats.csv')  # Replace with the path to your actual CSV file

# Filter rows where 'DMG Multiplier' is 'N/A'
filtered_df = df[df['DMG Multiplier'] == 'N/A']

# Save the filtered DataFrame to a new CSV file
filtered_df.to_csv('filtered_rows_with_na_dmg_multiplier.csv', index=False)

print("Filtered CSV file saved as 'filtered_rows_with_na_dmg_multiplier.csv'")