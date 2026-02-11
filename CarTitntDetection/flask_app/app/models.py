from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    """User model for registration and authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    organization = db.Column(db.String(120), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    test_results = db.relationship('TestResult', backref='user', lazy=True, cascade='all, delete-orphan')
    performance_logs = db.relationship('PerformanceLog', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class TestResult(db.Model):
    """Model to store detection test results"""
    __tablename__ = 'test_results'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    test_type = db.Column(db.String(50), nullable=False)  # 'image', 'video', 'webcam'
    file_path = db.Column(db.String(255), nullable=True)
    original_filename = db.Column(db.String(255), nullable=False)
    output_path = db.Column(db.String(255), nullable=True)
    
    # Detection Results
    windows_detected = db.Column(db.Integer, default=0)
    tinted_windows = db.Column(db.Integer, default=0)
    clear_windows = db.Column(db.Integer, default=0)
    
    # Confidence Metrics
    average_confidence = db.Column(db.Float, default=0.0)
    total_detections = db.Column(db.Integer, default=0)
    
    # Additional Info
    processing_time = db.Column(db.Float, nullable=True)  # in seconds
    model_version = db.Column(db.String(50), default="mkpc6-ctdz6/2")
    status = db.Column(db.String(50), default='completed')  # 'completed', 'failed', 'processing'
    error_message = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Raw prediction data (JSON)
    predictions_json = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<TestResult {self.id} - {self.test_type}>'


class PerformanceLog(db.Model):
    """Model to store performance metrics"""
    __tablename__ = 'performance_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Performance Metrics
    total_tests = db.Column(db.Integer, default=0)
    total_detections = db.Column(db.Integer, default=0)
    average_confidence = db.Column(db.Float, default=0.0)
    
    # Test Breakdown
    image_tests = db.Column(db.Integer, default=0)
    video_tests = db.Column(db.Integer, default=0)
    webcam_tests = db.Column(db.Integer, default=0)
    
    # Tinted vs Clear
    tinted_count = db.Column(db.Integer, default=0)
    clear_count = db.Column(db.Integer, default=0)
    
    # Performance
    avg_processing_time = db.Column(db.Float, default=0.0)
    max_processing_time = db.Column(db.Float, default=0.0)
    min_processing_time = db.Column(db.Float, default=0.0)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PerformanceLog {self.id} - User {self.user_id}>'
