import os
import secrets
from dotenv import load_dotenv

# Load environment variables from a .flaskenv file, typically used for configuration
load_dotenv('.flaskenv')

# Get the absolute path of the current directory
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # The Config class holds all configuration settings for the Flask app

    # Set a secret key, either from an environment variable or generate one if it's not found
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

    # Set the database URI, prioritizing an environment variable if present, otherwise using SQLite with a local file
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')

    # Disable SQLAlchemy modification tracking to save resources
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Specify the folder where uploaded files will be stored
    UPLOAD_FOLDER = 'app/static/uploads'

    # Limit the maximum size of file uploads to 16MB
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024


