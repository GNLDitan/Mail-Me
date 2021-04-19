from flask_login import UserMixin
from sqlalchemy.sql import func
from . import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    is_social_media = db.Column(db.Boolean)
    media_type = db.Column(db.String(150))

class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    subject = db.Column(db.String(5000))
    content = db.Column(db.String(5000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    isread = db.Column(db.Boolean)
    reply_id = db.Column(db.String(5000))

class Receiver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'))
    email = db.Column(db.String(150))

class Carboncopy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'))
    email = db.Column(db.String(150))