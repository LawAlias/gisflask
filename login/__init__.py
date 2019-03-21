
from extensions import login_manager
from flask import Flask
from main import app
def register_extensions(app):
    login_manager.init_app(app)
users = {'15764255859@163.com': {'password': '123'}}
register_extensions(app)
# app = Flask('login')

from login import views

