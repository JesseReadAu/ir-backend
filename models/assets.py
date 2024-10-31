from db import db

class Assets(db.Model):
    __tablename__ = 'assets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    category = db.Column(db.String(256))
    filetype = db.Column(db.String(256))
    filesize = db.Column(db.String(256))
    link = db.Column(db.String(256))
    screenshot = db.Column(db.String(256))
    user_id = db.Column(db.Integer())
