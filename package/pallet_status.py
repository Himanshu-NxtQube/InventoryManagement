import cv2
from ultralytics import YOLO
from package.config_loader import get_config

class PalletStatus:
    def __init__(self):
        self.CONFIG = get_config()
        self.pallet_status_estimator = YOLO(self.CONFIG["models"]["pallet_status_model"])

    def get_status(self, image_path, boundaries, img_dims, depth_map):
        left_line_x, right_line_x, upper_line_y, lower_line_y = boundaries
        center_w, center_h = img_dims[0]//2, img_dims[1]//2

        # Apply plasma colormap
        colored_depth = cv2.applyColorMap(depth_map, cv2.COLORMAP_PLASMA)

        results = self.pallet_status_estimator.predict(colored_depth, verbose=False)
        class_names = self.pallet_status_estimator.names

        left_boxes = []
        right_boxes = []

        for box in results[0].boxes:  # xyxy format: [x1, y1, x2, y2]
            # print(box.xyxy)
            x1, y1, x2, y2 = box.xyxy[0]
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            # Filter out within ROI
            if left_line_x < cx < right_line_x and upper_line_y < cy < lower_line_y:

                class_id = int(box.cls[0])            
                class_name = class_names[class_id]

                if cx < center_w:
                    left_boxes.append([cx, class_name])
                else:
                    right_boxes.append([cx, class_name])

        left_box_result = None
        right_box_result = None

        if left_boxes:
            left_box_result = min(left_boxes,key=lambda x:x[0])[1]
        if right_boxes:
            right_box_result = max(right_boxes,key=lambda x:x[0])[1]

        return left_box_result, right_box_result

