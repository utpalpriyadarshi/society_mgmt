# gui/profile_photo_widget.py
"""
Widget for handling resident profile photos in the GUI.
"""

from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QFileDialog, 
                             QVBoxLayout, QHBoxLayout, QMessageBox)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, pyqtSignal
import os
from utils.profile_photo_manager import profile_photo_manager


class ProfilePhotoWidget(QWidget):
    photoChanged = pyqtSignal(str)  # Signal emitted when photo changes
    
    def __init__(self, parent=None, resident_id=None):
        super().__init__(parent)
        self.resident_id = resident_id
        self.current_photo_path = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Photo display
        self.photo_label = QLabel()
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.photo_label.setMinimumSize(150, 150)
        self.photo_label.setMaximumSize(150, 150)
        self.photo_label.setStyleSheet("""
            QLabel {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                background-color: #ecf0f1;
            }
        """)
        self.set_placeholder_photo()
        
        # Buttons
        button_layout = QHBoxLayout()
        self.upload_button = QPushButton("Upload Photo")
        self.upload_button.clicked.connect(self.upload_photo)
        
        self.remove_button = QPushButton("Remove Photo")
        self.remove_button.clicked.connect(self.remove_photo)
        self.remove_button.setEnabled(False)
        
        button_layout.addWidget(self.upload_button)
        button_layout.addWidget(self.remove_button)
        
        layout.addWidget(self.photo_label)
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def set_placeholder_photo(self):
        """Set a placeholder photo when no photo is available."""
        self.photo_label.setText("No Photo")
        self.photo_label.setStyleSheet("""
            QLabel {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                background-color: #ecf0f1;
                color: #7f8c8d;
                font-size: 12px;
            }
        """)
    
    def set_photo(self, photo_filename):
        """Set the photo to display."""
        if not photo_filename:
            self.set_placeholder_photo()
            self.remove_button.setEnabled(False)
            return
            
        photo_path = profile_photo_manager.get_profile_photo_path(photo_filename)
        if photo_path and os.path.exists(photo_path):
            pixmap = QPixmap(photo_path)
            if not pixmap.isNull():
                # Scale the pixmap to fit the label while maintaining aspect ratio
                pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.photo_label.setPixmap(pixmap)
                self.photo_label.setStyleSheet("""
                    QLabel {
                        border: 1px solid #bdc3c7;
                        border-radius: 6px;
                        background-color: white;
                    }
                """)
                self.current_photo_path = photo_path
                self.remove_button.setEnabled(True)
                return
        
        # If we couldn't load the photo, show placeholder
        self.set_placeholder_photo()
        self.remove_button.setEnabled(False)
    
    def upload_photo(self):
        """Open file dialog to select and upload a photo."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Profile Photo", 
            "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            try:
                # Validate the file is actually an image
                image = QImage(file_path)
                if image.isNull():
                    QMessageBox.warning(self, "Invalid Image", "The selected file is not a valid image.")
                    return
                
                # Read the image data
                with open(file_path, "rb") as f:
                    photo_data = f.read()
                
                # Determine file extension
                _, ext = os.path.splitext(file_path)
                ext = ext.lower()
                
                # Save the photo
                photo_filename = profile_photo_manager.save_profile_photo(
                    self.resident_id, photo_data, ext
                )
                
                if photo_filename:
                    # Update the resident's photo path in the database
                    success = profile_photo_manager.update_resident_photo_path(
                        self.resident_id, photo_filename
                    )
                    
                    if success:
                        self.set_photo(photo_filename)
                        self.photoChanged.emit(photo_filename)
                        QMessageBox.information(self, "Success", "Profile photo uploaded successfully!")
                    else:
                        # Clean up the saved photo if database update failed
                        profile_photo_manager.delete_profile_photo(photo_filename)
                        QMessageBox.critical(self, "Error", "Failed to update resident record with photo.")
                else:
                    QMessageBox.critical(self, "Error", "Failed to save profile photo.")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to upload photo: {str(e)}")
    
    def remove_photo(self):
        """Remove the current photo."""
        if self.current_photo_path:
            # Extract filename from path
            photo_filename = os.path.basename(self.current_photo_path)
            
            # Remove from database
            success = profile_photo_manager.update_resident_photo_path(
                self.resident_id, None
            )
            
            if success:
                # Delete the photo file
                profile_photo_manager.delete_profile_photo(photo_filename)
                
                # Update UI
                self.set_placeholder_photo()
                self.current_photo_path = None
                self.remove_button.setEnabled(False)
                self.photoChanged.emit(None)
                QMessageBox.information(self, "Success", "Profile photo removed successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to remove photo from resident record.")
