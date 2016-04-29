# project/models.py


import datetime

from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy.orm import relationship

from project import db, app


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255))
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    items = relationship('Item')

    def __init__(self, email,name, admin=False):
        self.name = name
        self.email = email
        self.registered_on = datetime.datetime.now()
        self.admin = admin

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def hash_password(self, passw):
        self.password = pwd_context.encrypt(passw)

    def verify_password(self, passw):
        return pwd_context.verify(passw, self.password)

    def get_id(self):
        return self.id

    def __repr__(self):
        return {'id': self.id, 'name': self.name, 'email': self.email}

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, name, description, owner_id, url):
        self.name = name
        self.url = url
        self.description = description
        self.owner_id = owner_id

    def __repr__(self):
        return {'id': self.id, 'name': self.name, 'description': self.description, 'url': self.url,
                'user': self.user_id}
