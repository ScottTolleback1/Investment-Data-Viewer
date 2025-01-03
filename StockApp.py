from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QLineEdit, 
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
import yfinance as yf
from DB import DB  
from StockGraph import StockGraph  
from Generate_Company_names import Generate_Company_names



class StockApp(QMainWindow):
    def __init__(self, DB):
        super().__init__()
        self.setWindowTitle("Stock Tracker")
        self.setGeometry(100, 100, 800, 600)
        self.DB = DB
        self.gcn = Generate_Company_names()

        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)

        self.input_layout = QGridLayout()

        self.stock_input = QLineEdit()
        self.stock_input.setPlaceholderText("Enter Stock Ticker Symbol")
        self.input_layout.addWidget(self.stock_input, 0, 0)  # Row 0, Column 0

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter Amount (Number of Shares)")
        self.input_layout.addWidget(self.amount_input, 1, 0)  # Row 1, Column 0

        self.add_button = QPushButton("Add to Favorites")
        self.add_button.clicked.connect(self.add_to_favorites)
        self.input_layout.addWidget(self.add_button, 0, 1)  # Row 0, Column 1

        self.remove_button = QPushButton("Remove from Favorites")
        self.remove_button.clicked.connect(self.remove_from_favorites)
        self.input_layout.addWidget(self.remove_button, 1, 1)  # Row 1, Column 1

        self.search_button = QPushButton("Search stock")
        self.search_button.clicked.connect(self.search_stock)
        self.input_layout.addWidget(self.search_button, 2, 1)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter ticker to search stock")
        self.input_layout.addWidget(self.search_input, 2, 0)  

        self.main_layout.addLayout(self.input_layout)

        self.show_favorites_button = QPushButton("Update Favorite Stocks")
        self.show_favorites_button.clicked.connect(self.show_favorites)
        self.main_layout.addWidget(self.show_favorites_button)

        self.favorites_table = QTableWidget()
        self.main_layout.addWidget(self.favorites_table)

        self.setCentralWidget(self.central_widget)
        self.show_favorites()  

    def search_stock(self):
        ticker = self.search_input.text().strip().upper()
        if ticker:
            if not self.gcn.ticker_exist(ticker):
                ticker = self.gcn.match(ticker)
                if ticker != "No match found":
                    self.hide()
                    sg = StockGraph(ticker, self, "1y")
                    sg.show()
                else: 
                    QMessageBox.warning(self, "Input Error", "No matches was found.")
            else:
                self.hide()
                sg = StockGraph(ticker, self, "1y")
                sg.show()
            
            
        
        self.search_input.clear()
        self.search_input.setPlaceholderText("Enter ticker to search stock")

    def show_favorites(self):
        self.favorites_table.clear()
        favorites = self.DB.get_favorite_stocks()
        self.favorites_table.setRowCount(len(favorites))
        self.favorites_table.setColumnCount(6)
        self.favorites_table.setHorizontalHeaderLabels(["Name", "Ticker", "Current Price", "Amount", "Amount Value", "Change Today"])

        sorted_favorites = sorted(favorites, key=lambda x: x[0])
        for row, (ticker, amount) in enumerate(sorted_favorites):
            try:
                stock_data = self.find_stock(ticker)
                long_name = stock_data['long_name']
                current_price = stock_data['current_price']
                first_price = stock_data['change']
                diff = round(((current_price - first_price) / first_price) * 100, 2)

                for i in range(len(favorites)):
                    self.favorites_table.setColumnWidth(i, 125)

                self.favorites_table.setItem(row, 0, QTableWidgetItem(long_name))
                self.favorites_table.setItem(row, 1, QTableWidgetItem(ticker))
                self.favorites_table.setItem(row, 2, QTableWidgetItem(f"{current_price} $"))
                self.favorites_table.setItem(row, 3, QTableWidgetItem(str(amount)))
                self.favorites_table.setItem(row, 4, QTableWidgetItem(f"{round(float(current_price) * amount, 2)} $" if current_price != 'N/A' else 'N/A'))

                change_item = QTableWidgetItem(f"{str(diff)}%")
                self.favorites_table.setItem(row, 5, change_item)

                if diff > 0:
                    change_item.setForeground(QColor("green"))
                elif diff == 0:
                    change_item.setForeground(QColor("white"))
                else:
                    change_item.setForeground(QColor("red"))

            except Exception as e:
                QMessageBox.warning(self, "Data Error", f"Error fetching data for {ticker}.\n{e}")

    def add_to_favorites(self):
        ticker = self.stock_input.text().strip().upper()
        if not ticker:
            QMessageBox.warning(self, "Input Error", "Please enter a stock ticker symbol.")
            return

        if not self.gcn.ticker_exist(ticker):
            ticker = self.gcn.match(ticker)
        response = QMessageBox.question(self, "Confirm Action", f"Do you want to add {ticker} to favorites?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if response == QMessageBox.StandardButton.Yes:
            stock_data = yf.Ticker(ticker)
            info = stock_data.info
            stock_name = info.get('shortName', ticker)

            if 'regularMarketPreviousClose' in info:
                amount_str = self.amount_input.text().strip()

                if amount_str.isdigit():
                    amount = int(amount_str)
                    if amount > 0:
                        self.DB.add_favorite_stock(ticker, stock_name, amount)
                        QMessageBox.information(self, "Success", f"{amount} shares of {ticker} added to favorites.")

                        self.reset_inputs()

                        self.show_favorites()
                    else:
                        QMessageBox.warning(self, "Input Error", "Please enter a positive number for the amount.")
                else:
                    QMessageBox.warning(self, "Input Error", "Please enter a valid number for the amount.")
            else:
                QMessageBox.critical(self, "Error", f"Failed to add {ticker} to favorites.\nStock data not available.")
        else:
            QMessageBox.information(self, "Cancelled", f"{ticker} was not added to favorites.")

    def remove_from_favorites(self):
        ticker = self.stock_input.text().strip().upper()
        amount_str = self.amount_input.text().strip()
        if not ticker:
            QMessageBox.warning(self, "Input Error", "Please enter a stock ticker symbol.")
            return

        if amount_str.isdigit():
            amount = int(amount_str)
            self.DB.remove_favorite_stock(ticker, amount)
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
    
    def find_stock(self, stock):
        try:
            stock_data = yf.Ticker(stock)
            info = stock_data.info

            long_name = info.get('longName', stock) 
            current_price = round(info.get('regularMarketPrice') or info.get('currentPrice') or info.get('previousClose') or 'N/A', 2)
            change = info.get('regularMarketOpen') or info.get('regularMarketPrice') or info.get('previousClose') or 'N/A'
            return {
                'long_name': long_name,
                'current_price': current_price,
                'change' : change
            }

        except Exception as e:
            print(f"Error fetching data for stock {stock}: {e}")
            return {
                'long_name': stock,
                'current_price': 'N/A'
            }

    def closeEvent(self, event):
        QApplication.quit()  
        event.accept()

