from app import db
from datetime import datetime
import json

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    template = db.Column(db.String(50), default='classic')
    is_draft = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    full_name = db.Column(db.String(200))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    location = db.Column(db.String(200))
    summary = db.Column(db.Text)
    photo_path = db.Column(db.String(500))
    
    education_data = db.Column(db.Text)
    experience_data = db.Column(db.Text)
    skills_data = db.Column(db.Text)
    customization_data = db.Column(db.Text)
    portfolio_data = db.Column(db.Text)
    
    def get_education(self):
        return json.loads(self.education_data) if self.education_data else []
    
    def set_education(self, data):
        self.education_data = json.dumps(data, ensure_ascii=False)
    
    def get_experience(self):
        return json.loads(self.experience_data) if self.experience_data else []
    
    def set_experience(self, data):
        self.experience_data = json.dumps(data, ensure_ascii=False)
    
    def get_skills(self):
        return json.loads(self.skills_data) if self.skills_data else []
    
    def set_skills(self, data):
        self.skills_data = json.dumps(data, ensure_ascii=False)
    
    def get_customization(self):
        default = {
            'font': 'Arial',
            'primary_color': '#667eea',
            'secondary_color': '#764ba2',
            'sections': {
                'summary': True,
                'experience': True,
                'education': True,
                'skills': True
            }
        }
        if self.customization_data:
            try:
                return json.loads(self.customization_data)
            except:
                return default
        return default
    
    def set_customization(self, data):
        self.customization_data = json.dumps(data, ensure_ascii=False)
    
    def get_portfolio(self):
        return json.loads(self.portfolio_data) if self.portfolio_data else []
    
    def set_portfolio(self, data):
        self.portfolio_data = json.dumps(data, ensure_ascii=False)
    
    def get_completion_percentage(self):
        total_fields = 8
        filled = 0
        
        if self.full_name and self.full_name.strip():
            filled += 1
        if self.email and self.email.strip():
            filled += 1
        if self.phone and self.phone.strip():
            filled += 1
        if self.location and self.location.strip():
            filled += 1
        if self.summary and self.summary.strip():
            filled += 1
        if self.get_experience():
            filled += 1
        if self.get_education():
            filled += 1
        if self.get_skills():
            filled += 1
        
        return int((filled / total_fields) * 100)
    
    def __repr__(self):
        return f'<Resume {self.title}>'
