import cv2
import logging

class Utilities:
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
    
    def is_valid_image(self, image_path):
        width, height = self.get_image_dimensions(image_path)

        if width < height:
            logging.log(logging.WARN, "Vertical photo detected!")
