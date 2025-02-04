from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Config(db.Model):
    __tablename__ = 'configs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(100), nullable=False, unique=True)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get_default(cls):
        """Get the default config if one exists"""
        return cls.query.filter_by(is_default=True).first()

    @classmethod
    def set_default(cls, config_id):
        """Set a config as default and ensure no other config is default"""
        cls.query.filter_by(is_default=True).update({'is_default': False})
        cls.query.filter_by(id=config_id).update({'is_default': True})

    @classmethod
    def _create(cls, name: str, filename: str, is_default: bool = False) -> 'Config':
        """Internal method for config creation
        
        Args:
            name: Display name for the config
            filename: Name of the config file
            is_default: Whether this is the default config
            
        Returns:
            Created Config instance
        """
        return cls(
            name=name,
            filename=filename,
            is_default=is_default
        )

    def _to_dict(self) -> dict:
        """Convert config to dictionary
        
        Returns:
            Dictionary representation of config
        """
        return {
            'id': self.id,
            'name': self.name,
            'filename': self.filename,
            'is_default': self.is_default,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def __repr__(self):
        return f'<Config {self.name}>'

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
