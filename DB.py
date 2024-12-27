import sqlite3
import yfinance as yf

class DB():

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

        try:
            # Check if the stock already exists
            cursor.execute('''
            SELECT amount FROM favorite_stocks WHERE ticker_symbol = ?
            ''', (ticker_symbol,))
            row = cursor.fetchone()

            if row:
                # If the stock exists, add the current amount to the new amount
                current_amount = row[0]
                new_amount = current_amount + amount
                cursor.execute('''
                UPDATE favorite_stocks
                SET amount = ?, stock_name = ?
                WHERE ticker_symbol = ?
                ''', (new_amount, stock_name, ticker_symbol))
            else:
                # If the stock does not exist, insert it
                cursor.execute('''
                INSERT INTO favorite_stocks (ticker_symbol, stock_name, amount)
                VALUES (?, ?, ?)
                ''', (ticker_symbol, stock_name, amount))

            success = 1
            conn.commit()
        except Exception as e:
            print(f"An error occurred while adding {ticker_symbol}: {e}")
        finally:
            conn.close()

        return success


    def remove_favorite_stock(ticker_symbol, amount):
        conn = sqlite3.connect('stocks.db')
        cursor = conn.cursor()
        success = 0
        
        try:
            # Fetch the current amount
            cursor.execute('''
            SELECT amount FROM favorite_stocks WHERE ticker_symbol = ?
            ''', (ticker_symbol,))
            row = cursor.fetchone()
            
            if row:
                current_amount = row[0]
                
                # Subtract the amount
                new_amount = current_amount - amount
                
                if new_amount > 0:
                    # Update the amount in the database
                    cursor.execute('''
                    UPDATE favorite_stocks SET amount = ? WHERE ticker_symbol = ?
                    ''', (new_amount, ticker_symbol))
                    print(f"{ticker_symbol} updated successfully. New amount: {new_amount}")
                else:
                    # Remove the stock from the database if the amount becomes 0 or less
                    cursor.execute('''
                    DELETE FROM favorite_stocks WHERE ticker_symbol = ?
                    ''', (ticker_symbol,))
                    print(f"{ticker_symbol} removed successfully as the amount reached 0.")
                
                success = 1
            else:
                print(f"{ticker_symbol} not found in favorite_stocks.")
            
            conn.commit()
        except Exception as e:
            print(f"An error occurred while processing {ticker_symbol}: {e}")
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


