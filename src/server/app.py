import os
from flask import Flask
from server.extensions import db  # Importing db
from server.routes.stock_routes import stock_bp
from server.routes.user_routes import user_bp


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Load basic config
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY"),
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
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
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    app.config[
        "SQLALCHEMY_TRACK_MODIFICATIONS"
    ] = False  # Disable track modifications for performance reasons

    # Initialize the db with the app
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(stock_bp)
    app.register_blueprint(user_bp)

    return app
