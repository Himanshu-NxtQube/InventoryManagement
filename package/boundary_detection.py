from package.config_loader import get_config
from ultralytics import YOLO
import cv2

class BoundaryDetector:
    def __init__(self):
        """Initializes the unified model and thresholds from the configuration."""
        self.CONFIG = get_config()
        self.model = YOLO(self.CONFIG['models']['boundary_model'])
        self.boundary_threshold = self.CONFIG['thresholds']['boundary_model']['confidence_threshold']
        self.merge_threshold = self.CONFIG['thresholds']['boundary_model']['merge_threshold']
        

    def get_boundaries(self, image_path):
        """
        Detects blue and orange bars in the image and returns their boundary positions.

        Args:
            image_path (str): Path to the input image.

        Returns:
            Tuple[int, int, int, int]: (left_x, right_x, upper_y, lower_y)
        """
        image = self._load_image(image_path)
        # image = cv2.merge([cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)] * 3) # for b/w image
        img_height, img_width = image.shape[:2]

        results = self.model.predict(image, verbose=False)[0]
        blue_boxes = []
        orange_boxes = []

        for box in results.boxes:
            cls = int(box.cls.item())
            conf = box.conf.item()
            if conf < self.boundary_threshold:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            if cls == self.CONFIG['bars']['vertical']:
                center_x = (x1 + x2) // 2
                blue_boxes.append(center_x)
                # print('blue')
            elif cls == self.CONFIG['bars']['horizontal']:
                orange_boxes.append((y1, y2))
                # print('orange')
        #     cv2.circle(image, (int((x1+x2)/2), int((y1+y2)/2)), 10, (0,0,255), 10)
        # cv2.imwrite("annotations.png", image)
        # input()

        # Process blue bar: horizontal boundaries (X-axis)
        blue_boxes.sort()
        merged_centers = self._merge_close_centers(blue_boxes, self.merge_threshold)

        if len(merged_centers) == 0:
            print("⚠️ No blue bars detected. Using image edges.")
            left_x = 0
            right_x = img_width - 1
        elif len(merged_centers) == 1:
            center = merged_centers[0]
            if center < img_width // 2:
                print("⚠️ Only one blue bar on left side. Assuming right = image edge.")
                left_x = center
                right_x = img_width - 1
            else:
                print("⚠️ Only one blue bar on right side. Assuming left = image edge.")
                left_x = 0
                right_x = center
        else:
            left_x = merged_centers[0]
            right_x = merged_centers[-1]

        # Process orange bar: vertical boundaries (Y-axis)
        y_mid = img_height // 2
        upper = [y1 for y1, y2 in orange_boxes if y2 <= y_mid]
        lower = [y2 for y1, y2 in orange_boxes if y1 >= y_mid]

        if not upper:
            print("⚠️ No upper orange bar detected. Using top of image.")
        if not lower:
            print("⚠️ No lower orange bar detected. Using bottom of image.")

        upper_y = int(min(upper)) if upper else 0
        lower_y = int(max(lower)) if lower else img_height - 1

        return left_x, right_x, upper_y, lower_y

    def _load_image(self, path):
        """Loads an image from the provided path."""
        img = cv2.imread(path)
        if img is None:
            raise ValueError(f"Unable to load image from path: {path}")
        return img

    def _merge_close_centers(self, centers, min_distance):
        """
        Merges centers that are closer than the specified minimum distance.
        """
        merged = []
        for c in centers:
            if not merged or c - merged[-1] > min_distance:
                merged.append(c)
        return merged
