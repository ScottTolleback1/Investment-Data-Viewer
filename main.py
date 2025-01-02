# main.py
from StockApp import StockApp
from DB import DB
from PyQt6.QtWidgets import QApplication
import sys
import pandas as pd
import re


if __name__ == "__main__":
    # Create the database if it doesn't exist
    df = pd.read_csv('nasdaq.csv')

    # Open the text file to write the data
    with open('nasdaq', 'w') as file:
    # Iterate through each row of the DataFrame
        for index, row in df.iterrows():
            # Check if 'Common Stock' is in the Name column
            if 'Common Stock' in row['Name']:
                # Remove 'Common Stock', 'Inc', and 'Corporation' using regex
                company_name = re.sub(r'\b(Common Stock|Inc|Corporation)\b|\.','', row['Name'], flags=re.IGNORECASE)
                # Clean up any extra spaces
                company_name = company_name.strip()
                # Write the cleaned 'Name' and 'Symbol' columns to the file
                file.write(f"{company_name} ({row['Symbol']})\n")

    DB.create_db()

    # Initialize the Qt application
    app = QApplication(sys.argv)
    window = StockApp(DB)
    window.show()

    # Execute the application
    sys.exit(app.exec())
