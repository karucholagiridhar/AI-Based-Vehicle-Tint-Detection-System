#!/usr/bin/env python
"""
Test script to verify all required libraries are properly installed and can be imported.
"""

import sys

def test_imports():
    """Test all critical imports for the application"""
    
    print("=" * 60)
    print("TESTING ALL LIBRARY IMPORTS")
    print("=" * 60)
    
    print(f"\nPython Version: {sys.version}")
    print(f"Python Path: {sys.executable}\n")
    
    # Test core Flask dependencies
    print("Testing Core Flask Dependencies...")
    try:
        import flask
        print(f"✓ Flask: {flask.__version__}")
    except ImportError as e:
        print(f"✗ Flask: {e}")
        return False
    
    try:
        import flask_sqlalchemy
        print(f"✓ Flask-SQLAlchemy: Installed")
    except ImportError as e:
        print(f"✗ Flask-SQLAlchemy: {e}")
        return False
    
    try:
        from sqlalchemy import __version__ as sqlalchemy_version
        print(f"✓ SQLAlchemy: {sqlalchemy_version}")
    except ImportError as e:
        print(f"✗ SQLAlchemy: {e}")
        return False
    
    try:
        import werkzeug
        print(f"✓ Werkzeug: {werkzeug.__version__}")
    except ImportError as e:
        print(f"✗ Werkzeug: {e}")
        return False
    
    # Test AI/ML dependencies
    print("\nTesting AI/ML Dependencies...")
    try:
        import cv2
        print(f"✓ OpenCV: {cv2.__version__}")
    except ImportError as e:
        print(f"✗ OpenCV: {e}")
        return False
    
    try:
        import numpy as np
        print(f"✓ NumPy: {np.__version__}")
    except ImportError as e:
        print(f"✗ NumPy: {e}")
        return False
    
    try:
        import inference_sdk
        print(f"✓ Inference SDK: {inference_sdk.__version__}")
    except ImportError as e:
        print(f"✗ Inference SDK: {e}")
        return False
    
    try:
        from PIL import Image
        import PIL
        print(f"✓ Pillow: {PIL.__version__}")
    except ImportError as e:
        print(f"✗ Pillow: {e}")
        return False
    
    # Test application modules
    print("\nTesting Application Modules...")
    try:
        from app.inference import InferenceManager
        print("✓ InferenceManager: Imported successfully")
    except ImportError as e:
        print(f"✗ InferenceManager: {e}")
        return False
    
    try:
        from app.models import db, User, TestResult, PerformanceLog
        print("✓ Database Models: Imported successfully")
    except ImportError as e:
        print(f"✗ Database Models: {e}")
        return False
    
    try:
        from app.config import Config
        print("✓ Config: Imported successfully")
    except ImportError as e:
        print(f"✗ Config: {e}")
        return False
    
    # Test specific OpenCV functions used
    print("\nTesting OpenCV Functions...")
    try:
        # Test image processing functions
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        _ = cv2.cvtColor(test_img, cv2.COLOR_BGR2LAB)
        _ = cv2.GaussianBlur(test_img, (0, 0), 2.0)
        _ = cv2.createCLAHE(clipLimit=1.3, tileGridSize=(8,8))
        print("✓ OpenCV image processing functions: Working")
    except Exception as e:
        print(f"✗ OpenCV functions: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ ALL IMPORTS SUCCESSFUL!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
