from db import db

class Project_Assets(db.Model):
    __tablename__ = 'project_assets'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer)
    asset_id = db.Column(db.Integer)
