# Description: This file initializes the database for the Flask app.
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def connect_db(app):
    '''Connect db to Flask app'''
    db.init_app(app)