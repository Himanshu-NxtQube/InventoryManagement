from package.config_loader import get_config
from ultralytics import YOLO
from PIL import Image
import torch
from torchvision.ops import nms

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

        boxes = preds[0].boxes.xyxy.cpu()         # [N, 4]
        scores = preds[0].boxes.conf.cpu()        # [N]

        # Get image height
        with Image.open(image_path) as img:
            image_height = img.height

        min_cy_threshold = 0.2 * image_height

        # Filter by min_cy_threshold
        valid_boxes = []
        valid_scores = []

        for box, score in zip(boxes, scores):
            x1, y1, x2, y2 = box.tolist()
            cy = (y1 + y2) / 2
            if cy > min_cy_threshold:
                valid_boxes.append([x1, y1, x2, y2])
                valid_scores.append(score)

        if not valid_boxes:
            return []

        boxes_tensor = torch.tensor(valid_boxes)
        scores_tensor = torch.tensor(valid_scores)

        # Apply NMS (IoU threshold typically 0.4–0.6)
        keep_indices = nms(boxes_tensor, scores_tensor, iou_threshold=0.25)

        results = []
        for i in keep_indices:
            x1, y1, x2, y2 = boxes_tensor[i].int().tolist()
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)
            results.append(((x1, y1, x2, y2), (cx, cy)))
        # print(len(results))

        return results
