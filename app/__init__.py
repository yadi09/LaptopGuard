from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__, static_folder='static')  # Initialize Flask app
app.config.from_object(Config)  # Load configuration

db = SQLAlchemy(app)  # Set up database
migrate = Migrate(app, db)  # Enable database migrations

login = LoginManager(app)  # Manage user login sessions
login.login_view = 'login'  # Specify the login view


from app import routes, models  # Import routes and models
