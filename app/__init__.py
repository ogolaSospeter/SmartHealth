#This is my initialization of the app
from flask import Flask
import os

def start_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(__name__, template_folder=os.path.join(base_dir, '..', 'templates'),
                static_folder=os.path.join(base_dir, '..', 'static'))
    app.config.from_pyfile('config.py')

    return app