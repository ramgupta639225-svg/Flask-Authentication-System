from datetime import datetime

from app.extensions import db
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


class User(UserMixin, db.Model):
    __tablename__ = '_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    joined_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    password = db.Column(db.String(120))
    fullname = db.Column(db.String(120))
    bio = db.Column(db.String(200))
    picture = db.Column(db.String(200))


    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')


    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
