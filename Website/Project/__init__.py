from flask import Flask #to generate app from Flask 
from flask_sqlalchemy import SQLAlchemy #for database
import os # to get proper paths
from flask_migrate import Migrate #migrations for DBMS
from flask_login import LoginManager

# LoginManager : The login manager contains the code that lets your application and Flask-Login work together, such as how to load a user from an ID, where to send users when they need to log in, and the like.

from flask_mail import Mail

from flask_admin import Admin,AdminIndexView
from flask_admin.contrib.sqla import ModelView
# from .models import User

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__)) #basedir is given the complete path of (__init__.py) the file (__file__) this is written in

app.config['SECRET_KEY'] = 'somekey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'database.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL')
app.config['MAIL_PASSWORD'] = os.environ.get('PASS')

mail = Mail(app)

db = SQLAlchemy(app)
Migrate(app,db) #to make all the migrations to the database

loginmanager = LoginManager()
loginmanager.init_app(app)
loginmanager.login_view = 'users.login'


from Project.users.views import users
from Project.core.views import core
app.register_blueprint(users)
app.register_blueprint(core)



