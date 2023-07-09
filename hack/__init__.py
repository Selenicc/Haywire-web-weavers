import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app =  Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config['SECRET_KEY'] = 'secret'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['STRIPE_SECRET_KEY'] = 'sk_test_51MMRkOSEzPBlgs1CJdlZhhC2OCxiFs74QjzGnPWhP7ardKmClTYvbOakK3JRSs0erzLNxIpvWxL2KfBZ4gINAd3q003ReAG2bm'
app.config['STRIPE_PUBLISHABLE_KEY'] = 'pk_test_51MMRkOSEzPBlgs1Ck16EBWSuxXEjbbbOKRtsACj65hPmP2B2gfy1BeWYGsfOxp60IyZM7A40h8tJzTbgCHr1vVeC00kwxztzSQ'
db = SQLAlchemy(app)
Migrate(app,db)

def create_db(app):
    with app.app_context():
        db.create_all()