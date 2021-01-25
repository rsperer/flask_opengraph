from flask import Flask
from flask_executor import Executor
from flask_sqlalchemy import SQLAlchemy
import logging

app = Flask(__name__)
executor = Executor(app)

logging.basicConfig(level=logging.INFO)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

from flaskog import routes


