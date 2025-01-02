import pandas as pd

# Load the CSV file into a DataFrame
df = pd.read_csv('nasdaq.csv')

# Open the text file to write the data
with open('nasdaq', 'w') as file:
    # Iterate through each row of the DataFrame
    for index, row in df.iterrows():
        # Check if 'Common Stock' is in the Name column
        if 'Common Stock' in row['Name']:
            # Remove 'Common Stock' from the Name
            company_name = row['Name'].replace(' Common Stock', '')
            # Write the cleaned 'Name' and 'Symbol' columns to the file
            file.write(f"{company_name} ({row['Symbol']})\n")

print("Common stocks data has been written to nasdaq_common_stock.txt")
