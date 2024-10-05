import os
from flask import Flask, send_from_directory, request, jsonify
import yfinance as yf
from flask_sqlalchemy import SQLAlchemy
from decimal import Decimal


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    # Load basic config
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY'),
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    # If test config is provided, load it
    if test_config is not None:
        app.config.from_mapping(test_config)

    # Create instance folder
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    
    # Database configuration using environment variables
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable track modifications for performance reasons

    # Initialize SQLAlchemy
    db = SQLAlchemy(app)

    # Models
    class Users(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        money = db.Column(db.Integer, unique=False, nullable=False)

    class Users_Stocks(db.Model):
        __tablename__ = 'users_stocks'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        symbol = db.Column(db.String(4), unique=True, nullable=False)
        quantity = db.Column(db.Integer, unique=False, nullable=False)
        
    def __repr__(self):
        return f'<User {self.username}>'

    @app.route('/')
    def index():
        # Serve the index.html from the dist directory
        return send_from_directory('../../dist', 'index.html')

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/stock/<string:ticker>', methods=['GET'])
    def stock(ticker):
        try:
            res = yf.Ticker(ticker)
            stock_info = res.info
            if not stock_info:
                return jsonify({'error': 'Stock information not found'}), 404

            # Ensure stock_info is JSON serializable
            return jsonify(stock_info)
        except Exception as e:
            print(f"Error fetching stock data: {e}")
            return jsonify({'error': 'Failed to fetch stock data'}), 500

    @app.route('/buy', methods=['POST'])
    def buy():
        data = request.json

        # Validate the request data
        symbol = data.get('symbol')
        quantity = data.get('quantity')
        user_id = 1  # We only support a single user for now
        
        if not symbol or not isinstance(symbol, str):
            return jsonify({'error': 'Invalid stock symbol'}), 400

        if not isinstance(quantity, (int, float)) or quantity <= 0:
            return jsonify({'error': 'Invalid quantity'}), 400

        if not user_id or not isinstance(user_id, int):
            return jsonify({'error': 'Invalid user ID'}), 400

        # Check if the user exists
        user = Users.query.get(user_id)
        if not user:
            return jsonify({'error': 'User does not exist'}), 404

        # Fetch the current price of the stock (example using yfinance)
        stock_info = yf.Ticker(symbol).info
        if not stock_info or 'currentPrice' not in stock_info:
            return jsonify({'error': 'Failed to fetch stock price'}), 400

        stock_price = Decimal(stock_info['currentPrice'])  # Convert to Decimal
        total_cost = stock_price * Decimal(quantity)  # Convert quantity to Decimal as well

        # Check if the user has enough money
        if user.money < total_cost:
            return jsonify({'error': f'Insufficient funds. You need ${total_cost}, but have ${user.money}'}), 400

        # Deduct the total cost from the user's money
        print('yo sup', user.money, total_cost)
        user.money -= total_cost

        # Check if the user already owns this stock
        existing_stock = Users_Stocks.query.filter_by(user_id=user_id, symbol=symbol).first()
        
        if existing_stock:
            # Update the quantity if the stock already exists for this user
            existing_stock.quantity += quantity
        else:
            # Add a new entry to the Users_Stocks table
            new_stock = Users_Stocks(user_id=user_id, symbol=symbol, quantity=quantity)
            db.session.add(new_stock)

        # Commit the changes to the database
        db.session.commit()

        return jsonify({
            'message': f'Bought {quantity} shares of {symbol} for user {user_id}', 
            'remaining_money': user.money
        }), 200
        
    @app.route('/sell', methods=['POST'])
    def sell_stock():
        data = request.json

        # Validate the request data
        symbol = data.get('symbol')
        quantity = data.get('quantity')
        user_id = 1  # We only support a single user for now
        
        if not symbol or not isinstance(symbol, str):
            return jsonify({'error': 'Invalid stock symbol'}), 400

        if not isinstance(quantity, (int, float)) or quantity <= 0:
            return jsonify({'error': 'Invalid quantity'}), 400

        # Check if the user exists
        user = Users.query.get(user_id)
        if not user:
            return jsonify({'error': 'User does not exist'}), 404

        # Check if the user owns the stock
        existing_stock = Users_Stocks.query.filter_by(user_id=user_id, symbol=symbol).first()
        if not existing_stock:
            return jsonify({'error': f'User does not own any shares of {symbol}'}), 400

        # Ensure the user has enough stock to sell
        if existing_stock.quantity < quantity:
            return jsonify({'error': f'Insufficient stock quantity. You have {existing_stock.quantity} shares of {symbol}, but tried to sell {quantity}'}), 400

        # Fetch the current price of the stock (example using yfinance)
        stock_info = yf.Ticker(symbol).info
        if not stock_info or 'currentPrice' not in stock_info:
            return jsonify({'error': 'Failed to fetch stock price'}), 400

        stock_price = Decimal(stock_info['currentPrice'])  # Convert to Decimal
        total_sale_value = stock_price * Decimal(quantity)  # Convert quantity to Decimal as well

        # Increase the user's money based on the sale
        user.money += total_sale_value

        # Reduce the user's stock quantity
        existing_stock.quantity -= quantity

        # If the user sold all their shares, remove the stock from their portfolio
        if existing_stock.quantity == 0:
            db.session.delete(existing_stock)

        # Commit the changes to the database
        db.session.commit()

        return jsonify({
            'message': f'Sold {quantity} shares of {symbol} for user {user_id}', 
            'total_sale_value': str(total_sale_value),
            'remaining_money': str(user.money)
        }), 200


    @app.route('/stocks', methods=['GET'])
    def get_user_stocks():
        user_id = 1 # We only support a single user right now
        # Fetch all stocks owned by the user
        user_stocks = Users_Stocks.query.filter_by(user_id=user_id).all()
        if not user_stocks:
            return jsonify({'error': f'No stocks found for user {user_id}'}), 404

        # Convert the results into a JSON-serializable format
        stocks = [
            {'symbol': stock.symbol, 'quantity': stock.quantity}
            for stock in user_stocks
        ]

        return jsonify(stocks), 200

    @app.route('/money', methods=['GET'])
    def get_user_money():
        user_id = 1 # We only support a single user right now
        # Fetch user by id
        user = Users.query.get(user_id)
        
        if not user:
            return jsonify({'error': f'User with ID {user_id} not found'}), 404

        # Return the user's money
        return jsonify({'money': user.money}), 200

      
    # This app is only intended to support one user at the moment
    # Initialize with this route
    @app.route('/init_user', methods=['POST'])
    def init_user():
        existing_user = Users.query.get(1)
        
        if existing_user:
            return "User with ID 1 already exists, no new user created."
        new_user = Users(id=1, username="alex", money=1000000.00)
        db.session.add(new_user)
        db.session.commit()
        
        return "New user initialized"

    @app.route('/delete_all_users', methods=['DELETE'])
    def delete_all_users():
      Users.query.delete()
      db.session.commit()

    return app
