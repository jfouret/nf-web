from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Pipeline(db.Model):
    __tablename__ = 'pipelines'
    
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(50), nullable=False)  # github or gitlab
    org_name = db.Column(db.String(100), nullable=False)
    project_name = db.Column(db.String(100), nullable=False)
    ref = db.Column(db.String(255), default='main')
    ref_type = db.Column(db.String(20), default='branch')  # branch, tag, or commit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Pipeline {self.org_name}/{self.project_name}>'

    @staticmethod
    def init_db(app):
        """Initialize the database and create tables"""
        db.init_app(app)
        with app.app_context():
            db.create_all()
