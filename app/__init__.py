from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите в систему для доступа к этой странице.'
    
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.resume import bp as resume_bp
    app.register_blueprint(resume_bp, url_prefix='/resume')
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    from app.hh import bp as hh_bp
    app.register_blueprint(hh_bp, url_prefix='/hh')
    
    from app.integrations import bp as integrations_bp
    app.register_blueprint(integrations_bp, url_prefix='/integrations')
    
    from app.models.platform_connection import PlatformConnection, ResumePublication
    from app.models.api_settings import ApiSettings
    
    with app.app_context():
        db.create_all()
        create_admin_user()
    
    return app


def create_admin_user():
    from app.models.user import User
    
    admin_email = 'admin@mail.ru'
    admin = User.query.filter_by(email=admin_email).first()
    
    if not admin:
        admin = User(
            username='admin',
            email=admin_email,
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user created: {admin_email}")
    elif not admin.is_admin:
        admin.is_admin = True
        db.session.commit()
        print(f"Admin privileges granted to: {admin_email}")
