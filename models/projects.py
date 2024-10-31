from db import db

class Projects(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    type = db.Column(db.String(256))
    client = db.Column(db.String(256))
    date_start = db.Column(db.String(256))
    date_end = db.Column(db.String(256))
    user_id = db.Column(db.Integer())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "client": self.client,
            "date_start": self.date_start,
            "date_end": self.date_end,
            "user_id": self.user_id
        }