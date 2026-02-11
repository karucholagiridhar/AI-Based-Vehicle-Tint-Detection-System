"""
Car Tint Detection Flask Application
Real-Time Detection of Black-Tinted Vehicle Glasses Using AI
"""

import os
import sys
from app import create_app, db
from app.models import User, TestResult, PerformanceLog

# Create Flask app
app = create_app(os.environ.get('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    """Add models to shell context"""
    return {
        'db': db,
        'User': User,
        'TestResult': TestResult,
        'PerformanceLog': PerformanceLog
    }


@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print('✓ Database initialized successfully')


if __name__ == '__main__':
    with app.app_context():
        # Ensure tables exist
        db.create_all()
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
