from google.cloud import vision
from package.config_loader import get_config
import os
import io

class OCRClient:
        
    def __init__(self):
        self.CONFIG = get_config()
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.CONFIG['google_vision_client']['credentials']
        self.client = vision.ImageAnnotatorClient()
    
    def get_annotations(self, image_path: str):
        # image = cv2.imread(image_path)
        # if image is None:
        #     raise ValueError(f"Error loading image: {image_path}")

        # # Convert image to bytes for Google Vision API
        # _, image_encoded = cv2.imencode('.jpg', image)
        # content = image_encoded.tobytes()
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
        response = self.client.text_detection(image=vision.Image(content=content))
        annotations = response.text_annotations
        return annotations
    
if __name__=='__main__':
    ocr_client = OCRClient()
    res = ocr_client.get_annotations('annotations.png')
    print(res)