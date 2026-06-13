import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_dropzone import Dropzone
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from elasticsearch import Elasticsearch

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'Sick Rat')
app.config['ENQUIRY_RECIPIENT'] = os.getenv('ENQUIRY_RECIPIENT', 'hnengare@gmail.com')
app.config['ELASTICSEARCH_URL'] = os.getenv('ELASTICSEARCH_URL')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.png', '.jpg', '.jpeg', '.gif', 'webp']
app.config['DROPZONE_UPLOAD_MULTIPLE'] = True
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_INPUT_NAME'] = 'file'
app.config['DROPZONE_MAX_FILES'] = 5 * 1024
app.config['DROPZONE_TIMEOUT'] = 45
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image/*'
app.config['UPLOAD_PATH'] = os.getcwd() + '/app/static/uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///site.db')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.getenv('MY_EMAIL')
app.config['MAIL_PASSWORD'] = os.getenv('MY_MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True


db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)
bcrypt = Bcrypt(app)
dropzone = Dropzone(app)
login_manager = LoginManager(app)
mail = Mail(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Elasticsearch is optional: when no URL is configured, search falls back to
# in-memory filtering (see app/utilities). The client is lazy — constructing it
# does not require a reachable server.
es = Elasticsearch(app.config['ELASTICSEARCH_URL']) if app.config['ELASTICSEARCH_URL'] else None
ELASTICSEARCH_INDEX = 'listings'

# Schema is managed by Flask-Migrate (`flask db upgrade`); no import-time create_all().

from app import routes, models, forms