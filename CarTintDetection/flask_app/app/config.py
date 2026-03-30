import os
from datetime import timedelta


class Config:
    """Base configuration"""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database - Support SQLite (dev), MySQL, and PostgreSQL (production)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///car_tint_detection.db'
    # Fix for Heroku postgres:// -> postgresql://
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    
    # Upload
    _default_upload = '/var/data/uploads' if os.environ.get('RENDER') == 'true' else os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or _default_upload
    # Keep default conservative to avoid platform proxy 413 responses; override via env if needed.
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'mp4', 'avi', 'mov', 'mkv'}
    
    # API - Use environment variables with fallback to development values
    ROBOFLOW_API_URL = os.environ.get('ROBOFLOW_API_URL', "https://detect.roboflow.com")
    ROBOFLOW_API_KEY = os.environ.get('ROBOFLOW_API_KEY', "cto2SFwA0t7Z5g5qqOQi")
    MODEL_ID = os.environ.get('MODEL_ID', "tinted-car-windows-mkpc6-ctdz6/2")
    
    # Image Processing
    MAX_IMAGE_WIDTH = 1280
    DISPLAY_WIDTH = 600
    DISPLAY_HEIGHT = 420


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
