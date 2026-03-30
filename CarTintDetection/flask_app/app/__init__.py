from flask import Flask
from app.models import db
from app.config import config_by_name
import os


def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__, 
                static_folder=os.path.join(os.path.dirname(__file__), 'static'),
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
    
    # Load configuration
    app.config.from_object(config_by_name.get(config_name, 'development'))
    
    # Create upload directory if it doesn't exist
    upload_folder = app.config.get('UPLOAD_FOLDER')
    if upload_folder and not os.path.exists(upload_folder):
        try:
            os.makedirs(upload_folder, exist_ok=True)
            app.logger.info(f'Created upload folder: {upload_folder}')
        except Exception as e:
            app.logger.warning(f'Could not create upload folder {upload_folder}: {e}')
    
    # Initialize database
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    from app.auth_routes import auth_bp
    from app.main_routes import main_bp
    from app.profile_api import profile_api
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(profile_api)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500
    
    return app
