"""
Simple test to check if assets are accessible in executable
"""
import sys
import os

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        print("Running as executable, _MEIPASS: {}".format(base_path))
    except Exception:
        base_path = os.path.abspath(".")
        print("Running in development, base_path: {}".format(base_path))
    
    full_path = os.path.join(base_path, relative_path)
    print("Looking for resource at: {}".format(full_path))
    exists = os.path.exists(full_path)
    print("File exists: {}".format(exists))
    
    if exists:
        print("File size: {} bytes".format(os.path.getsize(full_path)))
    
    return full_path, exists

print("=== Asset Accessibility Test ===")

# Test if we're running as executable
try:
    print("_MEIPASS: {}".format(sys._MEIPASS))
except:
    print("Not running as executable")

# Test asset files
assets_to_test = [
    "assets/nextgenlogo.png",
    "assets/SocietyImage1.jpg"
]

for asset in assets_to_test:
    print("\n--- Testing {} ---".format(asset))
    path, exists = get_resource_path(asset)
    
    if exists:
        # Try to load with QPixmap to verify it's a valid image
        try:
            from PyQt5.QtGui import QPixmap
            pixmap = QPixmap(path)
            if pixmap.isNull():
                print("ERROR: File exists but is not a valid image")
            else:
                print("SUCCESS: Valid image, size: {}x{}".format(pixmap.width(), pixmap.height()))
        except Exception as e:
            print("ERROR: Could not load image: {}".format(e))
    else:
        print("ERROR: File not found")

print("\n=== Test Complete ===")