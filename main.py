# main.py
from StockApp import StockApp
from DB import DB
from PyQt6.QtWidgets import QApplication
import sys
import pandas as pd
import re


if __name__ == "__main__":
    df = pd.read_csv('nasdaq.csv')

    with open('nasdaq', 'w') as file:
        for index, row in df.iterrows():
            if 'Common Stock' in row['Name']:
                company_name = re.sub(r'\b(Common Stock|Inc|Corporation)\b|\.','', row['Name'], flags=re.IGNORECASE)
                company_name = company_name.strip()
                file.write(f"{company_name} ({row['Symbol']})\n")

    DB.create_db()

    app = QApplication(sys.argv)
    window = StockApp(DB)
    window.show()

    sys.exit(app.exec())
