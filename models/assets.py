from db import db
from flask import jsonify
class Assets(db.Model):
    __tablename__ = 'assets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    category = db.Column(db.String(256))
    filetype = db.Column(db.String(256))
    filesize = db.Column(db.Float())
    link = db.Column(db.String(256))
    screenshot = db.Column(db.String(256))
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=True)

    def __init__(self, name, category, filetype, filesize, link, screenshot, user_id):
        self.name = name
        self.category = category
        self.filetype = filetype
        self.filesize = filesize
        self.link = link
        self.screenshot = screenshot
        self.user_id = user_id

    #Develop Overview as json
    def __repr__(self):
        return jsonify({"id": self.id, "name": self.name, "category": self.category})