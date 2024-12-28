from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QComboBox, QLabel, QSizePolicy
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
        
        self.combo_box = QComboBox()
        self.combo_box.addItems(["1d", "1mo", "1y"])
        self.combo_box.currentTextChanged.connect(self.plot_stock_graph)
        self.main_layout.addWidget(self.combo_box)

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
