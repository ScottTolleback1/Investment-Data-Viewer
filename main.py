# main.py
from StockApp import StockApp
from DB import DB
from PyQt6.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    # Create the database if it doesn't exist
    DB.create_db()

    # Initialize the Qt application
    app = QApplication(sys.argv)
    window = StockApp(DB)
    window.show()

    # Execute the application
    sys.exit(app.exec())
