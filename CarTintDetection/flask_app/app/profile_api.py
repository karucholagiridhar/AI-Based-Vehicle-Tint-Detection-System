"""
Profile Management API Routes
Handles profile updates and password changes
"""

from flask import Blueprint, request, jsonify, session
from functools import wraps
from app.models import db, User
from app.auth_routes import validate_email, validate_password
import re

profile_api = Blueprint('profile_api', __name__, url_prefix='/api/profile')


def api_login_required(f):
    """Decorator for API authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Get current authenticated user"""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None


def validate_phone(phone):
    """Validate phone number format"""
    # Allow digits, spaces, dashes, parentheses, and plus sign
    pattern = r'^[\d\s\-\(\)\+]{10,15}$'
    return re.match(pattern, phone) is not None


@profile_api.route('/update', methods=['POST'])
@api_login_required
def update_profile():
    """
    Update user profile information
    
    Request JSON:
    {
        "full_name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890",
        "organization": "My Company"
    }
    
    Response JSON:
    {
        "success": true,
        "message": "Profile updated successfully",
        "user": {
            "username": "johndoe",
            "email": "john@example.com",
            "full_name": "John Doe",
            "phone": "+1234567890",
            "organization": "My Company"
        }
    }
    """
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        data = request.get_json()
        
        # Validate required fields
        full_name = data.get('full_name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        organization = data.get('organization', '').strip()
        
        if not all([full_name, email, phone]):
            return jsonify({
                'success': False,
                'error': 'Full name, email, and phone are required'
            }), 400
        
        # Validate email format
        if not validate_email(email):
            return jsonify({
                'success': False,
                'error': 'Invalid email format'
            }), 400
        
        # Validate phone format
        if not validate_phone(phone):
            return jsonify({
                'success': False,
                'error': 'Invalid phone number format'
            }), 400
        
        # Check if email is already taken by another user
        if email != user.email:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return jsonify({
                    'success': False,
                    'error': 'Email already registered to another account'
                }), 400
        
        # Update user fields
        user.full_name = full_name
        user.email = email
        user.phone = phone
        user.organization = organization
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'user': {
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'phone': user.phone,
                'organization': user.organization
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@profile_api.route('/change-password', methods=['POST'])
@api_login_required
def change_password():
    """
    Change user password
    
    Request JSON:
    {
        "current_password": "oldpass123",
        "new_password": "newpass456",
        "confirm_password": "newpass456"
    }
    
    Response JSON:
    {
        "success": true,
        "message": "Password changed successfully"
    }
    """
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        data = request.get_json()
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        # Validate all fields provided
        if not all([current_password, new_password, confirm_password]):
            return jsonify({
                'success': False,
                'error': 'All password fields are required'
            }), 400
        
        # Verify current password
        if not user.check_password(current_password):
            return jsonify({
                'success': False,
                'error': 'Current password is incorrect'
            }), 400
        
        # Check if new passwords match
        if new_password != confirm_password:
            return jsonify({
                'success': False,
                'error': 'New passwords do not match'
            }), 400
        
        # Validate new password strength
        valid, msg = validate_password(new_password)
        if not valid:
            return jsonify({
                'success': False,
                'error': msg
            }), 400
        
        # Check if new password is different from current
        if current_password == new_password:
            return jsonify({
                'success': False,
                'error': 'New password must be different from current password'
            }), 400
        
        # Update password
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@profile_api.route('/get', methods=['GET'])
@api_login_required
def get_profile():
    """
    Get current user profile data
    
    Response JSON:
    {
        "success": true,
        "user": {
            "id": 1,
            "username": "johndoe",
            "email": "john@example.com",
            "full_name": "John Doe",
            "phone": "+1234567890",
            "organization": "My Company",
            "created_at": "2026-01-15T10:30:00"
        }
    }
    """
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'phone': user.phone,
                'organization': user.organization,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500
