from flask import Flask
from flask_cors import CORS
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from Chatbot.chatbot import Chatbot

app = Flask(__name__)
app.config.from_object(Config)

# create db object representing the database
db = SQLAlchemy(app)  

# create object to represent migration engine
migrate = Migrate(app, db)

# create Flask-Login instance to manage login state and remember which users are logged in as they navigate pages
login = LoginManager(app)
login.login_view = 'login'
login.session_protection = None

# create Chatbot instance
chatbot = Chatbot()

CORS(app);

from app import routes, models

