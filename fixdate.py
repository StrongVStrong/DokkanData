import pandas as pd

# Load the CSV
df = pd.read_csv('final_data.csv')

# Initialize a variable to store the last "Base" release date
last_base_release_date = None

# Iterate over the rows
for index, row in df.iterrows():
    # Check if the current row is of type "Base"
    if row['State'] == 'Base':
        last_base_release_date = row['Release Date']
    
    # If the current row is of type "Transformation", update the release date
    elif row['State'] == 'Transformation' and last_base_release_date is not None:
        df.at[index, 'Release Date'] = last_base_release_date

# Save the modified DataFrame back to a new CSV
df.to_csv('truefinaldata.csv', index=False)
print("Saved updated data to 'truefinaldata.csv'")