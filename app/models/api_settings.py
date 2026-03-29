from app import db
from datetime import datetime


class ApiSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), unique=True, nullable=False)
    client_id = db.Column(db.String(256))
    client_secret = db.Column(db.String(256))
    redirect_uri = db.Column(db.String(512))
    is_active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    updated_by = db.relationship('User', backref='api_settings_updates')
    
    @classmethod
    def get_settings(cls, platform):
        return cls.query.filter_by(platform=platform, is_active=True).first()
    
    @classmethod
    def get_hh_settings(cls):
        return cls.get_settings('hh')
    
    @classmethod
    def get_superjob_settings(cls):
        return cls.get_settings('superjob')
    
    def __repr__(self):
        return f'<ApiSettings {self.platform}>'
