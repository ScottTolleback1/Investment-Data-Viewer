from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QLineEdit, 
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt
import yfinance as yf
from DB import DB


class StockApp(QMainWindow):
    def __init__(self, DB):
        super().__init__()
        self.setWindowTitle("Stock Tracker")
        self.setGeometry(100, 100, 800, 600)
        self.DB = DB
                # Main layout
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)

        # Input layout (use QGridLayout for grid-style alignment)
        self.input_layout = QGridLayout()

        # Stock input
        self.stock_input = QLineEdit()
        self.stock_input.setPlaceholderText("Enter Stock Ticker Symbol")
        self.input_layout.addWidget(self.stock_input, 0, 0)  # Row 0, Column 0

        # Amount input
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter Amount (Number of Shares)")
        self.input_layout.addWidget(self.amount_input, 1, 0)  # Row 0, Column 1

        # Add to Favorites Button
        self.add_button = QPushButton("Add to Favorites")
        self.add_button.clicked.connect(self.add_to_favorites)
        self.input_layout.addWidget(self.add_button, 0, 1)  # Row 1, Column 0

        # Remove from Favorites Button
        self.remove_button = QPushButton("Remove from Favorites")
        self.remove_button.clicked.connect(self.remove)
        self.input_layout.addWidget(self.remove_button, 1, 1)  # Row 1, Column 1

        # Add the input layout to the main layout
        self.main_layout.addLayout(self.input_layout)

        # Stock Info Label
        self.stock_info_label = QLabel("Stock Information will appear here.")
        self.stock_info_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.main_layout.addWidget(self.stock_info_label)

        # Show Favorites Button
        self.show_favorites_button = QPushButton("Show Favorite Stocks")
        self.show_favorites_button.clicked.connect(self.show_favorites)
        self.main_layout.addWidget(self.show_favorites_button)

        # Favorites Table
        self.favorites_table = QTableWidget()
        self.main_layout.addWidget(self.favorites_table)

        self.setCentralWidget(self.central_widget)
        self.show_favorites()

        

    def show_favorites(self):
        self.favorites_table.clear()
        favorites = DB.get_favorite_stocks()
        self.favorites_table.setRowCount(len(favorites))
        self.favorites_table.setColumnCount(5)
        self.favorites_table.setHorizontalHeaderLabels(["Name", "Ticker", "Current Price","Amount", "Amount Value"])
        sorted_favorites = sorted(favorites, key=lambda x: x[0])
        for row, (ticker, amount) in enumerate(sorted_favorites):
            try:
                stock_data = DB.find_stock(ticker)
                long_name = stock_data['long_name']
                current_price = stock_data['current_price']

                self.favorites_table.setItem(row, 0, QTableWidgetItem(long_name))
                self.favorites_table.setItem(row, 1, QTableWidgetItem(ticker))
                self.favorites_table.setItem(row, 2, QTableWidgetItem(str(current_price) + " $"))
                self.favorites_table.setItem(row, 3, QTableWidgetItem(str(amount)))
                self.favorites_table.setItem(row, 4, QTableWidgetItem(str(float(current_price) * amount) + " $" if current_price != 'N/A' else 'N/A') )

            except Exception as e:
                QMessageBox.warning(self, "Data Error", f"Error fetching data for {ticker}.\n{e}")


    def add_to_favorites(self):
        ticker = self.stock_input.text().strip().upper()
        if not ticker:
            QMessageBox.warning(self, "Input Error", "Please enter a stock ticker symbol.")
            return

        # Ask the user if they want to add the stock to favorites
        response = QMessageBox.question(self, "Confirm Action", f"Do you want to add {ticker} to favorites?", 
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if response == QMessageBox.StandardButton.Yes:
            stock_data = yf.Ticker(ticker)
            info = stock_data.info
            stock_name = info.get('shortName', ticker)

            # Check if stock information is valid
            if 'regularMarketPreviousClose' in info:
                # Get the amount entered by the user
                amount_str = self.amount_input.text().strip()

                if amount_str.isdigit():
                    amount = int(amount_str)
                    if amount > 0:
                        # Add the stock to favorites with the entered amount
                        DB.add_favorite_stock(ticker, stock_name, amount)
                        QMessageBox.information(self, "Success", f"{amount} shares of {ticker} added to favorites.")
                        
                        # Reset inputs
                        self.reset_inputs()
                        
                        # Refresh favorites
                        self.show_favorites()
                    else:
                        QMessageBox.warning(self, "Input Error", "Please enter a positive number for the amount.")
                else:
                    QMessageBox.warning(self, "Input Error", "Please enter a valid number for the amount.")
            else:
                QMessageBox.critical(self, "Error", f"Failed to add {ticker} to favorites.\nStock data not available.")
        else:
            QMessageBox.information(self, "Cancelled", f"{ticker} was not added to favorites.")

    def remove(self):
        ticker = self.stock_input.text().strip().upper()
        amount_str = self.amount_input.text().strip()
        if not ticker:
            QMessageBox.warning(self, "Input Error", "Please enter a stock ticker symbol.")
            return

        if amount_str.isdigit():
            amount = int(amount_str)
            DB.remove_favorite_stock(ticker, amount)
            QMessageBox.information(self, "Success", f"{amount} shares of {ticker} removed from favorites.")
            
            # Reset inputs
            self.reset_inputs()
            
            # Refresh favorites
            self.show_favorites()
        else:
            QMessageBox.warning(self, "Input Error", "Please enter a valid number for the amount.")

    def reset_inputs(self):
        self.stock_input.clear()
        self.stock_input.setPlaceholderText("Enter Stock Ticker Symbol")
        
        self.amount_input.clear()
        self.amount_input.setPlaceholderText("Enter Amount (Number of Shares)")
