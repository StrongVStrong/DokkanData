import csv
import re

# Input and output file paths
input_file = "dokkan_character_details_test.csv"  # Replace with your input file
output_file = "processed_datax.csv"

# Open the input file
with open(input_file, 'r') as infile:
    reader = csv.DictReader(infile)  # Read the CSV as dictionaries
    rows = list(reader)  # Store all rows in a list

# Open the output file
with open(output_file, 'w', newline='') as outfile:
    # Use the same headers as the input file
    headers = reader.fieldnames
    writer = csv.DictWriter(outfile, fieldnames=headers)
    writer.writeheader()  # Write the header row

    # Process each row
    for row in rows:
        # Extract and modify Leader Skill
        row["Leader Skill"] = row["Leader Skill"].replace("Leader Skill ", "").rstrip('"').strip()
        row["Leader Skill"] = row["Leader Skill"].replace("(Extreme) ", "").replace("(Super Extreme) ", "").strip()

        # Extract and modify Passive Skill
        row["Passive Skill"] = row["Passive Skill"].replace("Passive Skill ", "").rstrip('"').strip()
        row["Passive Skill"] = row["Passive Skill"].replace("(Extreme) ", "").replace("(Super Extreme) ", "").strip()

        # Parse and modify Stats
        stats = row["Stats 55% 100%"]
        if stats:  # Ensure Stats field is not empty
            stat_parts = stats.split('|')

            # Function to parse stats
            def get_values(stat_line):
                numbers = re.findall(r'\d[\d,]*', stat_line)  # Find all numbers
                if len(numbers) >= 4:  # If 4 or more values exist
                    return numbers[2], numbers[3]  # 3rd and 4th values
                elif len(numbers) == 2:  # If only 2 values exist
                    return numbers[1], numbers[1]  # Use the last value for both
                else:
                    return "0", "0"  # Default to placeholder if no valid values

            # Extract HP, ATK, DEF values
            hp_55, hp_100 = get_values(stat_parts[1]) if "HP" in stat_parts[1] else ("0", "0")
            atk_55, atk_100 = get_values(stat_parts[2]) if "ATK" in stat_parts[2] else ("0", "0")
            def_55, def_100 = get_values(stat_parts[3]) if "DEF" in stat_parts[3] else ("0", "0")

            # Rebuild the Stats column with only the 55% and 100% values
            row["Stats 55% 100%"] = f"HP {hp_55} {hp_100} | ATK {atk_55} {atk_100} | DEF {def_55} {def_100}"
        else:
            row["Stats 55% 100%"] = "HP 0 0 | ATK 0 0 | DEF 0 0"  # Placeholder for missing stats

        # Write the modified row to the output file
        writer.writerow(row)

print(f"Data has been processed and saved to {output_file}")
