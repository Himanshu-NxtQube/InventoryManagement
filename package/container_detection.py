from package.config_loader import get_config
from ultralytics import YOLO
from PIL import Image

class ContainerDetector:
    def __init__(self):
        self.CONFIG = get_config()
        self.model = YOLO(self.CONFIG['models']['container_model'])

    # def get_detections(self, image_path):

    #     conf_threshold = self.CONFIG['thresholds']['box_model']['confidence_threshold']
    #     preds = self.model(image_path, conf=conf_threshold, verbose=False)
    #     xyxy = preds[0].boxes.xyxy.cpu().numpy()  # [[x1,y1,x2,y2], ...]

    #     results = []
    #     for (x1, y1, x2, y2) in xyxy:
    #         cx = int( (x1 + x2) / 2 )
    #         cy = int( (y1 + y2) / 2 )
    #         bbox = (int(x1), int(y1), int(x2), int(y2))
    #         results.append((bbox, (cx, cy)))
            

    #     return results

      # or use cv2 if preferred

    def get_detections(self, image_path):
        conf_threshold = self.CONFIG['thresholds']['box_model']['confidence_threshold']
        preds = self.model(image_path, conf=conf_threshold, verbose=False)
        xyxy = preds[0].boxes.xyxy.cpu().numpy()  # [[x1,y1,x2,y2], ...]

        # Get image height
        with Image.open(image_path) as img:
            image_height = img.height

        min_cy_threshold = 0.2 * image_height

        results = []
        for (x1, y1, x2, y2) in xyxy:
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            if cy > min_cy_threshold:
                bbox = (int(x1), int(y1), int(x2), int(y2))
                results.append((bbox, (cx, cy)))

        return results
