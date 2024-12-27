import sys
import sqlite3
import yfinance as yf
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QLabel, QLineEdit, QMessageBox, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt


def create_db():
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS favorite_stocks (
        ticker_symbol TEXT PRIMARY KEY,
        stock_name TEXT,
        amount INTEGER
    )
    ''')
    conn.commit()
    conn.close()


def add_favorite_stock(ticker_symbol, stock_name, amount):
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()
    success = 0
    if stock_name is not None:
        cursor.execute('''
        INSERT OR REPLACE INTO favorite_stocks (ticker_symbol, stock_name, amount)
        VALUES (?, ?, ?)
        ''', (ticker_symbol, stock_name, amount))
        success = 1
        
    conn.commit()
    conn.close()
    return success

def remove_favorite_stock(ticker_symbol):
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()
    success = 0
    try:
        # Execute the DELETE statement
        cursor.execute('''
        DELETE FROM favorite_stocks WHERE ticker_symbol = ?
        ''', (ticker_symbol,))
        
        # Check if a row was deleted
        if cursor.rowcount > 0:
            success = 1
            print(f"{ticker_symbol} removed successfully.")
        else:
            print(f"{ticker_symbol} not found in favorite_stocks.")
        
        conn.commit()
    except Exception as e:
        print(f"An error occurred while removing {ticker_symbol}: {e}")
    finally:
        conn.close()
    
    return success


def get_favorite_stocks():
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT ticker_symbol, amount FROM favorite_stocks')
    favorites = cursor.fetchall()
    conn.close()
    return favorites


def find_stock(stock):
    try:
        # Fetch stock data
        stock_data = yf.Ticker(stock)
        info = stock_data.info

        # Extract long name and current price
        long_name = info.get('longName', stock)    # Use ticker as fallback if longName is unavailable
        current_price = info.get('regularMarketPrice') or info.get('currentPrice') or info.get('previousClose') or 'N/A'

        # Return only long name and current price
        return {
            'long_name': long_name,
            'current_price': current_price
        }

    except Exception as e:
        print(f"Error fetching data for stock {stock}: {e}")
        return {
            'long_name': stock,
            'current_price': 'N/A'
        }


class StockApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stock Tracker")
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)

        # Stock input
        self.stock_input = QLineEdit()
        self.stock_input.setPlaceholderText("Enter Stock Ticker Symbol")
        self.layout.addWidget(self.stock_input)

        # Amount input
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter Amount (Number of Shares)")
        self.layout.addWidget(self.amount_input)

        # Add to Favorites Button
        self.add_button = QPushButton("Add to Favorites")
        self.add_button.clicked.connect(self.add_to_favorites)
        self.layout.addWidget(self.add_button)

        # Add to Favorites Button
        self.remove_button = QPushButton("Remove from Favorites")
        self.remove_button.clicked.connect(self.remove)
        self.layout.addWidget(self.remove_button)

        # Stock Info Label
        self.stock_info_label = QLabel("Stock Information will appear here.")
        self.stock_info_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(self.stock_info_label)

        # Show Favorites Button
        self.show_favorites_button = QPushButton("Show Favorite Stocks")
        self.show_favorites_button.clicked.connect(self.show_favorites)
        self.layout.addWidget(self.show_favorites_button)

        # Favorites Table
        self.favorites_table = QTableWidget()
        self.layout.addWidget(self.favorites_table)

        self.setCentralWidget(self.central_widget)

    def show_favorites(self):
        self.favorites_table.clear()
        favorites = get_favorite_stocks()
        self.favorites_table.setRowCount(len(favorites))
        self.favorites_table.setColumnCount(5)
        self.favorites_table.setHorizontalHeaderLabels(["Name", "Ticker", "Current Price","Amount", "Amount Value"])

        for row, (ticker, amount) in enumerate(favorites):
            try:
                stock_data = find_stock(ticker)
                long_name = stock_data['long_name']
                current_price = stock_data['current_price']

                self.favorites_table.setItem(row, 0, QTableWidgetItem(long_name))
                self.favorites_table.setItem(row, 1, QTableWidgetItem(ticker))
                self.favorites_table.setItem(row, 2, QTableWidgetItem(str(current_price)))
                self.favorites_table.setItem(row, 3, QTableWidgetItem(str(amount)))
                self.favorites_table.setItem(row, 4, QTableWidgetItem(str(float(current_price) * amount) if current_price != 'N/A' else 'N/A'))

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
                        add_favorite_stock(ticker, stock_name, amount)
                        QMessageBox.information(self, "Success", f"{amount} shares of {ticker} added to favorites.")
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
        if not ticker:
            QMessageBox.warning(self, "Input Error", "Please enter a stock ticker symbol.")
            return
        remove_favorite_stock(ticker)
        self.show_favorites()

    

if __name__ == "__main__":
    create_db()
    app = QApplication(sys.argv)
    window = StockApp()
    window.show()
    sys.exit(app.exec())
