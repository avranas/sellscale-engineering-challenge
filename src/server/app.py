import os
from flask import Flask, send_file

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    app.config['FLASK_DEBUG'] = os.getenv('FLASK_DEBUG')
    print('hi there', os.getenv('FLASK_DEBUG'))

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        return send_file('../../dist/index.html')

    @app.route('/hello')
    def hello():
        return 'Hello, World!@@@@@@@@@@@'

    return app
