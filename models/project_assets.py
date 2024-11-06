from db import db

class Project_Assets(db.Model):
    __tablename__ = 'project_assets'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("Projects.id"))
    asset_id = db.Column(db.Integer, db.ForeignKey("Assets.id"))

    def __init__(self, project_id, asset_id):
        self.project_id = project_id
        self.asset_id = asset_id