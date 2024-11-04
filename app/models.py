from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import datetime
from app import db
from datetime import date

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    role = db.Column(db.Integer)

    def __init__(self, email, password, name, role):
        self.email = email
        self.password = password
        self.name = name
        self.role = role
        
        
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    filename = db.Column(db.String(200))
    size = db.Column(db.String(100))
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.now)

    def __init__(self, user_id, filename, size, created_at):
        self.user_id = user_id
        self.filename = filename
        self.size = size
        self.created_at = created_at