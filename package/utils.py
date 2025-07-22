from PIL import Image

class Utilities:
    def get_image_dimensions(self, image_path):
        with Image.open(image_path) as img:
            return img.size  # (width, height)
        
    def get_center_from_dimensions(width, height):
        """Returns the center (x, y) coordinates of an image given width and height."""
        center_x = width / 2
        center_y = height / 2
        return center_x, center_y