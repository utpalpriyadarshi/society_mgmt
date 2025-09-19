import os
import sys
from PIL import Image, ImageDraw

def create_icon():
    # Create a simple icon image
    size = (64, 64)
    image = Image.new('RGB', size, color=(73, 109, 137))
    draw = ImageDraw.Draw(image)
    
    # Draw a simple building-like structure
    draw.rectangle([10, 30, 20, 60], fill=(255, 255, 255))  # Left building
    draw.rectangle([25, 20, 35, 60], fill=(255, 255, 255))  # Middle building
    draw.rectangle([40, 35, 50, 60], fill=(255, 255, 255))  # Right building
    
    # Draw windows
    for x in [12, 16, 27, 31, 42, 46]:
        for y in [35, 45, 55]:
            draw.rectangle([x, y, x+2, y+2], fill=(255, 255, 0))
    
    # Save as ICO
    image.save('assets/icon.ico', format='ICO')

if __name__ == "__main__":
    create_icon()