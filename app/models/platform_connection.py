from app import db
from datetime import datetime
import json

class PlatformConnection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)
    refresh_token_encrypted = db.Column(db.Text)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    external_resume_id = db.Column(db.String(200))
    external_resume_url = db.Column(db.String(500))
    hh_resume_id = db.Column(db.String(50))
    
    __table_args__ = (db.UniqueConstraint('user_id', 'platform', name='unique_user_platform'),)
    
    def is_token_valid(self):
        if not self.access_token:
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        return True
    
    def set_refresh_token(self, token):
        from app.services.encryption_service import encrypt_token
        self.refresh_token_encrypted = encrypt_token(token)
    
    def get_refresh_token(self):
        from app.services.encryption_service import decrypt_token
        return decrypt_token(self.refresh_token_encrypted)
    
    def __repr__(self):
        return f'<PlatformConnection {self.platform} for user {self.user_id}>'


class ResumePublication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    external_id = db.Column(db.String(200))
    external_url = db.Column(db.String(500))
    status = db.Column(db.String(50), default='pending')
    error_message = db.Column(db.Text)
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ResumePublication {self.platform} status={self.status}>'
