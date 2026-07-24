from flask import Flask
from app.extensions import db, login_manager, mail
from app.models import User
from app.auth.routes import auth
from config import Config




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    app.register_blueprint(auth)
    return app

