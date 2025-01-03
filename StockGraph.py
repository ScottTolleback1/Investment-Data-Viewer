from PyQt6.QtWidgets import QApplication, QPushButton, QHBoxLayout, QMainWindow, QVBoxLayout, QWidget, QComboBox, QLabel, QSizePolicy
from PyQt6.QtGui import QGuiApplication
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import yfinance as yf


class StockGraph(QMainWindow):
    def __init__(self, ticker, parent, time):
        super().__init__(parent)  # Pass the parent window to be able to show it later
        self.setWindowTitle("Stock Graph Viewer")
        self.setGeometry(100, 100, 800, 600)
        self.ticker = ticker.strip().upper()

        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)

        self.stock_data = yf.Ticker(ticker)
        self.info = self.stock_data.info
        self.button_layout = QHBoxLayout()
        self.period = time
        periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
        for pe in periods:
            button = QPushButton(pe)  
            button.clicked.connect(lambda _, p=pe: self.plot_stock_graph(p, self.stock_data))
            self.button_layout.addWidget(button)
        


        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.main_layout.addWidget(self.canvas)

        self.setCentralWidget(self.central_widget)
        
        
        self.plot_stock_graph(self.period, self.stock_data)
        self.info_layout = QHBoxLayout()
        self.c_p = round(self.info.get('regularMarketPrice') or self.info.get('currentPrice') or self.info.get('previousClose') or 'N/A', 2)
        today_change = self.info.get('regularMarketOpen') or self.info.get('regularMarketPrice') or self.info.get('previousClose') or 'N/A'
        diff = round(((self.c_p - today_change) / today_change) * 100, 2)
        try:
            dividend_yield = self.info.get('dividendYield', None)  
            dividend_yield = str(round(dividend_yield * 100), 2) + "%"  
        except Exception as e:
            dividend_yield = "N/A" 

        self.main_layout.addLayout(self.button_layout)
        
        self.info_layout = QVBoxLayout()

        self.rating_label = QLabel("Dividend Yield: " + str(dividend_yield))
        self.price_label = QLabel("Current Price: " + str(self.c_p) + " $")
        self.change_label = QLabel("Change Today: " + str(diff) + "%")

        # Add first row of labels to the info_layout
        first_row_layout = QHBoxLayout()

        first_row_layout.addWidget(self.rating_label)
        first_row_layout.addWidget(self.price_label)
        first_row_layout.addWidget(self.change_label)
        if diff > 0:
            self.change_label.setStyleSheet("color: green;")
        elif diff < 0:
            self.change_label.setStyleSheet("color: red;")
        else:
            self.change_label.setStyleSheet("color: white;")

        self.info_layout.addLayout(first_row_layout)


        # Create second row layout (QHBoxLayout)
        second_row_layout = QHBoxLayout()

        pb_ratio = round(self.info.get('priceToBook', 'Data not available'),2 )
        pe_ratio = round(self.info.get('trailingPE', 'Data not available'),2 )

        historical_data = self.stock_data.history(period=self.period)

        if len(historical_data) >= 2:
            close_prices = historical_data['Close']

            latest_close = self.c_p
            
            previous_close = close_prices.iloc[0]

            difference = latest_close - previous_close
            t_change = round((difference / previous_close) * 100, 2)

        new_label_1 = QLabel("P/B: " + str(pb_ratio))
        new_label_2 = QLabel("P/E: " + str(pe_ratio))
        self.change_time = QLabel("Change   " + self.period + ": " + str(t_change) + "%")

        second_row_layout.addWidget(new_label_1)
        second_row_layout.addWidget(new_label_2)
        second_row_layout.addWidget(self.change_time)

        self.info_layout.addLayout(second_row_layout)

        self.main_layout.addLayout(self.info_layout)


        
        #here
  

    def plot_stock_graph(self, period, stock_data):
        try:
            historical_data = stock_data.history(period=period)
            if period == "1d":
                historical_data = stock_data.history(period=period, interval="1m")
            
            self.figure.clear()
            ax = self.figure.add_subplot(111)

            ax.set_facecolor("black")  
            self.figure.patch.set_facecolor("black")  

            ax.plot(historical_data.index, historical_data['Close'], color="lime", label="Closing Price", linestyle='-', linewidth=2)

            ax.legend(facecolor='black', edgecolor='white', labelcolor='white')


            ax.set_title(f"{self.ticker} - Last {period}", color="white")
            ax.set_ylabel("USD", color="white")

           # ax.tick_params(axis ='x', colors="white")
            ax.tick_params(axis='y', colors="white")
            
            ax.grid(color="gray", linestyle="--", linewidth=0.5)

         
        

            self.canvas.draw()
           
        except Exception as e:
            print(f"Error: {e}")



    def closeEvent(self, event):
        self.parent().show() 
        event.accept()  