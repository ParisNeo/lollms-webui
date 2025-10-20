# Lollms function call definition file
# File Name: draw_bounding_boxes.py
# Author: Saif (ParisNeo)
# Description: This script defines a function that takes an image file path and a list of bounding boxes in the form of x, y, w, h in normalized mode along with the labels, and returns the bounding boxes placed on top of the images with the labels.

# Lollms function call definition file
from functools import partial
from typing import List, Tuple
from lollms.utilities import PackageManager
from ascii_colors import trace_exception
from pathlib import Path

# Ensure necessary packages are installed
if not PackageManager.check_package_installed("Pillow"):
    PackageManager.install_package("Pillow")

from PIL import Image, ImageDraw, ImageFont

def draw_bounding_boxes(image_path: str, bounding_boxes: List[Tuple[float, float, float, float, str]]) -> str:
    """
    Draws bounding boxes on an image and saves the result.
    
    Args:
        image_path (str): Path to the input image file.
        bounding_boxes (List[Tuple[float, float, float, float, str]]): List of bounding boxes in normalized coordinates (x, y, w, h) along with labels.
        
    Returns:
        str: Path to the output image file with bounding boxes drawn.
    """
    try:
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Load the image
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        # Iterate over bounding boxes and draw them
        for bbox in bounding_boxes:
            x, y, w, h, label = bbox
            left = x * width
            top = y * height
            right = left + (w * width)
            bottom = top + (h * height)
            
            # Draw rectangle
            draw.rectangle([left, top, right, bottom], outline="red", width=2)
            
            # Draw label
            font = ImageFont.load_default()
            text_size = draw.textsize(label, font=font)
            text_background = [left, top - text_size[1], left + text_size[0], top]
            draw.rectangle(text_background, fill="red")
            draw.text((left, top - text_size[1]), label, fill="white", font=font)
        
        # Save the output image
        output_path = image_path.with_name(f"{image_path.stem}_with_boxes{image_path.suffix}")
        image.save(output_path)
        
        return str(output_path)
    except Exception as e:
        return trace_exception(e)

def draw_bounding_boxes_function():
    return {
        "function_name": "draw_bounding_boxes",
        "function": draw_bounding_boxes,
        "function_description": "Draws bounding boxes on an image and saves the result.",
        "function_parameters": [
            {"name": "image_path", "type": "str"},
            {"name": "bounding_boxes", "type": "List[Tuple[float, float, float, float, str]]"}
        ]
    }
