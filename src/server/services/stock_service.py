import yfinance as yf
from decimal import Decimal


def get_stock_price(symbol):
    stock_info = yf.Ticker(symbol).info
    if not stock_info or "currentPrice" not in stock_info:
        return None
    return Decimal(stock_info["currentPrice"])
