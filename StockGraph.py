from PyQt6.QtWidgets import QApplication, QPushButton, QHBoxLayout, QMainWindow, QVBoxLayout, QWidget, QComboBox, QLabel, QSizePolicy
from PyQt6.QtGui import QGuiApplication
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import yfinance as yf
import sys


class StockGraph(QMainWindow):
    def __init__(self, ticker, parent):
        super().__init__(parent)  # Pass the parent window to be able to show it later
        self.setWindowTitle("Stock Graph Viewer")
        self.setGeometry(100, 100, 800, 600)
        self.ticker = ticker.strip().upper()

        # Main layout
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)

        # Label and combo box
        self.label = QLabel(f"Stock: {self.ticker}")
        self.main_layout.addWidget(self.label)
        
        self.button_layout = QHBoxLayout()
        periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
        # Create buttons
        for period in periods:
            button = QPushButton(period)  # Button text as the period
            button.clicked.connect(lambda _, p=period: self.plot_stock_graph(p))
            self.button_layout.addWidget(button)
                # Add the button layout to the main layout
        self.main_layout.addLayout(self.button_layout)


        # Matplotlib figure and canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.main_layout.addWidget(self.canvas)

        self.setCentralWidget(self.central_widget)

        # Plot the stock graph for the initial period
        self.plot_stock_graph("1y")

    def plot_stock_graph(self, period):
        try:
            stock_data = yf.Ticker(self.ticker)
            historical_data = stock_data.history(period=period)
            if period is "1d":
                historical_data = stock_data.history(period=period, interval="1m")
            

            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.plot(historical_data.index, historical_data['Close'], label="Closing Price")
            ax.set_title(f"{self.ticker} - Last {period}")
            ax.set_xlabel("Date")
            ax.set_ylabel("Price (USD)")
            ax.legend()
            ax.grid()

            self.canvas.draw()

        except Exception as e:
            print(f"Error: {e}")

    def closeEvent(self, event):
        # Show the parent window again after closing the StockGraph window
        self.parent().show()  # parent() returns the main window (StockApp)
        event.accept()  # Accept the event and close the window
