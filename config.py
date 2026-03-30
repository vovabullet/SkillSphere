import os

class Config:
    SECRET_KEY = os.environ.get('SESSION_SECRET') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///resume_platform.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    APP_LOG_LEVEL = os.environ.get('APP_LOG_LEVEL', 'INFO')
    APP_LOG_PATH = os.environ.get('APP_LOG_PATH')
