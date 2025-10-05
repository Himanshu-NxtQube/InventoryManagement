import os
import cv2
import logging
from package.error_buffer import ErrorBuffer
from package.error_codes import ErrorCodes

class Utilities:
    def __init__(self):
        self.error_buffer = ErrorBuffer()
    def get_image_dimensions(self, image_path):
        """Returns image dimensions (width, height) using OpenCV."""
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Could not read image at {image_path}")
        height, width = img.shape[:2]
        return width, height
        
    def get_center_from_dimensions(self, width, height):
        """Returns the center (x, y) coordinates of an image given width and height."""
        center_x = width / 2
        center_y = height / 2
        return center_x, center_y
    
    def check_image_resolution(self, image_path, target_width, target_height):
        width, height = self.get_image_dimensions(image_path)

        if width < height:
            # logging.warning(
            #     "\n" + "-" * 50 +
            #     f"\n⚠️  Vertical Image Detected"
            #     f"\n   • Error Code : 502"
            #     f"\n   • File       : {os.path.basename(image_path)}"
            #     f"\n   • Resolution : {width} x {height}"
            #     f"\n   • Expected   : {target_width} x {target_height}"
            #     + "\n" + "-" * 50
            # )
            self.error_buffer.add_error(image_path=image_path, error=ErrorCodes.LOW_IMAGE_RESOLUTION)


        elif width < target_width and height < target_height:
            # logging.warning(
            #     "\n" + "-" * 50 +
            #     f"\n⚠️  Low Resolution Image Detected"
            #     f"\n   • Error Code : 502"
            #     f"\n   • File       : {os.path.basename(image_path)}"
            #     f"\n   • Resolution : {width} x {height}"
            #     f"\n   • Expected   : {target_width} x {target_height}"
            #     + "\n" + "-" * 50
            # )
            self.error_buffer.add_error(image_path=image_path, error=ErrorCodes.LOW_IMAGE_RESOLUTION)

