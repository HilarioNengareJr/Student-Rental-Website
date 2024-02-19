import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_dropzone import Dropzone
from flask_login import LoginManager
from flask_mail import Mail


app = Flask(__name__)

app.config['SECRET_KEY'] = 'Sick Rat'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.png', '.jpg', '.jpeg', '.gif', 'webp']
app.config['DROPZONE_UPLOAD_MULTIPLE'] = True
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_INPUT_NAME'] = 'file'
app.config['DROPZONE_MAX_FILES'] = 5 * 1024
app.config['DROPZONE_TIMEOUT'] = 45
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image/*'
app.config['UPLOAD_PATH'] = os.getcwd() + '/app/static/uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.getenv('MY_EMAIL')
app.config['MAIL_PASSWORD'] = os.getenv('MY_MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
dropzone = Dropzone(app)
login_manager = LoginManager(app)
mail = Mail(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

with app.app_context():
    db.create_all()

from app import routes, models, forms