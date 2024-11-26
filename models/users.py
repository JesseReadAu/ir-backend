from db import db

class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(256))
    last_name = db.Column(db.String(256))
    email = db.Column(db.String(256), unique=True)
    password = db.Column(db.String(256))
    session = db.Column(db.String(256))
    enabled = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime)

    def __init__(self, first_name, last_name, email, password, session, enabled):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.session = session
        self.enabled = enabled

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "password": self.password,
            "session": self.session,
            "enabled": self.enabled
        }

    def return_name(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name
        }

