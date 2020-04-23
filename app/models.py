from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, login
from flask_login import UserMixin



class User(UserMixin, db.Model):
  #User class inherits from db.Model (base class for all models in SQLAlchemy)
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(64), index=True, unique=True)
  password_hash = db.Column(db.String(128))
  messages = db.relationship('Message', backref='author', lazy='dynamic')
  userData = db.relationship('UserData', backref='author', lazy='dynamic')

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)

  #__repr__ method defines how to print objects in this class
  def __repr__(self):
    return '<User {}>'.format(self.username)


@login.user_loader
def load_user(id):
  if id is None or id == 'None':
    id = -1
  print('ID: ' + str(id) + ', leaving load_user')
  return User.query.get(int(id))


class Message(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  body = db.Column(db.String(140))
  timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
  order = db.Column(db.Integer)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

  def __repr__(self):
    return '<Message {}>'.format(self.body)

class UserData(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  messagesSent = db.Column(db.Integer)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

  def __repr__(self):
    return '<UserData {}>'.format(self.messagesSent)

