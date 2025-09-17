# utils/profile_photo_manager.py
"""
Utility module for managing resident profile photos.
"""

import os
import shutil
from PIL import Image
import hashlib
from datetime import datetime


class ProfilePhotoManager:
    def __init__(self, base_path="resident_photos"):
        """
        Initialize the ProfilePhotoManager.
        
        Args:
            base_path (str): Base directory for storing profile photos
        """
        self.base_path = base_path
        # Create the directory if it doesn't exist
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
    
    def save_profile_photo(self, resident_id, photo_data, file_extension=".jpg"):
        """
        Save a profile photo for a resident.
        
        Args:
            resident_id (int): ID of the resident
            photo_data (bytes): Photo data
            file_extension (str): File extension for the photo
            
        Returns:
            str: Path to the saved photo, or None if failed
        """
        try:
            # Generate a unique filename using resident ID and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"resident_{resident_id}_{timestamp}{file_extension}"
            photo_path = os.path.join(self.base_path, filename)
            
            # Save the photo data to file
            with open(photo_path, "wb") as f:
                f.write(photo_data)
            
            # Create a thumbnail for faster loading in lists
            self._create_thumbnail(photo_path)
            
            return filename
        except Exception as e:
            print(f"Error saving profile photo: {e}")
            return None
    
    def _create_thumbnail(self, photo_path, size=(100, 100)):
        """
        Create a thumbnail for a photo.
        
        Args:
            photo_path (str): Path to the original photo
            size (tuple): Size of the thumbnail (width, height)
        """
        try:
            # Create thumbnail filename
            base_name = os.path.basename(photo_path)
            name, ext = os.path.splitext(base_name)
            thumbnail_name = f"{name}_thumb{ext}"
            thumbnail_path = os.path.join(self.base_path, thumbnail_name)
            
            # Create and save thumbnail
            with Image.open(photo_path) as img:
                img.thumbnail(size)
                img.save(thumbnail_path)
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
    
    def get_profile_photo_path(self, photo_filename):
        """
        Get the full path to a profile photo.
        
        Args:
            photo_filename (str): Name of the photo file
            
        Returns:
            str: Full path to the photo, or None if not found
        """
        if not photo_filename:
            return None
            
        photo_path = os.path.join(self.base_path, photo_filename)
        return photo_path if os.path.exists(photo_path) else None
    
    def delete_profile_photo(self, photo_filename):
        """
        Delete a profile photo.
        
        Args:
            photo_filename (str): Name of the photo file to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not photo_filename:
                return True
                
            # Delete the main photo
            photo_path = os.path.join(self.base_path, photo_filename)
            if os.path.exists(photo_path):
                os.remove(photo_path)
            
            # Delete the thumbnail if it exists
            name, ext = os.path.splitext(photo_filename)
            thumbnail_name = f"{name}_thumb{ext}"
            thumbnail_path = os.path.join(self.base_path, thumbnail_name)
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
                
            return True
        except Exception as e:
            print(f"Error deleting profile photo: {e}")
            return False
    
    def update_resident_photo_path(self, resident_id, photo_filename, db_path="society_management.db"):
        """
        Update the profile photo path in the database for a resident.
        
        Args:
            resident_id (int): ID of the resident
            photo_filename (str): Name of the photo file
            db_path (str): Path to the database file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import sqlite3
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE residents SET profile_photo_path = ? WHERE id = ?",
                    (photo_filename, resident_id)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating resident photo path in database: {e}")
            return False

# Create a global instance for easy access
profile_photo_manager = ProfilePhotoManager()
