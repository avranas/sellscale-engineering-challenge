from flask import Blueprint, jsonify, request
from server.models.stock import Users_Stocks
from server.models.users import Users
from server.services.stock_service import get_stock_price
from server.extensions import db
from decimal import Decimal
import yfinance as yf

stock_bp = Blueprint("stock_bp", __name__)


@stock_bp.route("/stock/<string:ticker>", methods=["GET"])
def stock(ticker):
    try:
        res = yf.Ticker(ticker)
        stock_info = res.info
        if not stock_info:
            return jsonify({"error": "Stock information not found"}), 404
        return jsonify(stock_info)
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return jsonify({"error": "Failed to fetch stock data"}), 500


@stock_bp.route("/buy", methods=["POST"])
def buy():
    data = request.json

    # Validate the request data
    symbol = data.get("symbol")
    quantity = data.get("quantity")
    user_id = 1  # We only support a single user for now

    if not symbol or not isinstance(symbol, str):
        return jsonify({"error": "Invalid stock symbol"}), 400
    if not isinstance(quantity, (int, float)) or quantity <= 0:
        return jsonify({"error": "Invalid quantity"}), 400
    if not user_id or not isinstance(user_id, int):
        return jsonify({"error": "Invalid user ID"}), 400

    # Check if the user exists
    user = Users.query.get(user_id)
    if not user:
        return jsonify({"error": "User does not exist"}), 404

    # Fetch the current price of the stock (example using yfinance)
    stock_info = yf.Ticker(symbol).info
    if not stock_info or "currentPrice" not in stock_info:
        return jsonify({"error": "Failed to fetch stock price"}), 400

    # Convert to Decimal
    stock_price = Decimal(stock_info["currentPrice"])
    total_cost = stock_price * Decimal(quantity)

    # Check if the user has enough money
    if user.money < total_cost:
        return (
            jsonify(
                {
                    "error": f"Insufficient funds. You need ${total_cost}, but have ${user.money}"
                }
            ),
            400,
        )

    # Deduct the total cost from the user's money
    user.money -= total_cost

    # Check if the user already owns this stock
    existing_stock = Users_Stocks.query.filter_by(
        user_id=user_id, symbol=symbol
    ).first()

    if existing_stock:
        # Update the quantity if the stock already exists for this user
        existing_stock.quantity += quantity
    else:
        # Add a new entry to the Users_Stocks table
        new_stock = Users_Stocks(user_id=user_id, symbol=symbol, quantity=quantity)
        db.session.add(new_stock)

    # Commit the changes to the database
    db.session.commit()

    return (
        jsonify(
            {
                "message": f"Bought {quantity} shares of {symbol} for user {user_id}",
                "remaining_money": user.money,
            }
        ),
        200,
    )


@stock_bp.route("/sell", methods=["POST"])
def sell_stock():
    data = request.json

    # Validate the request data
    symbol = data.get("symbol")
    quantity = data.get("quantity")
    user_id = 1  # We only support a single user for now

    if not symbol or not isinstance(symbol, str):
        return jsonify({"error": "Invalid stock symbol"}), 400
    if not isinstance(quantity, (int, float)) or quantity <= 0:
        return jsonify({"error": "Invalid quantity"}), 400

    # Check if the user exists
    user = Users.query.get(user_id)
    if not user:
        return jsonify({"error": "User does not exist"}), 404

    # Check if the user owns the stock
    existing_stock = Users_Stocks.query.filter_by(
        user_id=user_id, symbol=symbol
    ).first()
    if not existing_stock:
        return jsonify({"error": f"User does not own any shares of {symbol}"}), 400

    # Ensure the user has enough stock to sell
    if existing_stock.quantity < quantity:
        return (
            jsonify(
                {
                    "error": f"Insufficient stock quantity. You have {existing_stock.quantity} shares of {symbol}, but tried to sell {quantity}"
                }
            ),
            400,
        )

    # Fetch the current price of the stock
    stock_info = yf.Ticker(symbol).info
    if not stock_info or "currentPrice" not in stock_info:
        return jsonify({"error": "Failed to fetch stock price"}), 400

    # Convert to Decimal
    stock_price = Decimal(stock_info["currentPrice"])
    total_sale_value = stock_price * Decimal(quantity)

    # Increase the user's money based on the sale
    user.money += total_sale_value

    # Reduce the user's stock quantity
    existing_stock.quantity -= quantity

    # If the user sold all their shares, remove the stock from their portfolio
    if existing_stock.quantity == 0:
        db.session.delete(existing_stock)

    # Commit the changes to the database
    db.session.commit()

    return (
        jsonify(
            {
                "message": f"Sold {quantity} shares of {symbol} for user {user_id}",
                "total_sale_value": str(total_sale_value),
                "remaining_money": str(user.money),
            }
        ),
        200,
    )


@stock_bp.route("/stocks", methods=["GET"])
def get_user_stocks():
    user_id = 1  # We only support a single user right now

    # Fetch all stocks owned by the user
    user_stocks = Users_Stocks.query.filter_by(user_id=user_id).all()
    if not user_stocks:
        return jsonify({"error": f"No stocks found for user {user_id}"}), 404

    # Convert the results into a JSON-serializable format
    stocks = [
        {"symbol": stock.symbol, "quantity": stock.quantity} for stock in user_stocks
    ]

    return jsonify(stocks), 200
