from package.pallet_status import PalletStatus
from ultralytics import YOLO
import torchvision.ops as ops
from package.config_loader import get_config
import pandas as pd
import cv2


class RackStackValidator:
    
    def __init__(self):
        self.CONFIG = get_config()
        self.model = YOLO(self.CONFIG['models']['box_model'])
        df_loaded = pd.read_csv(self.CONFIG['input']['stack_levels_csv'])

        # Create dictionary with format {Batch ID: Stack Level}
        self.REF_DICT = dict(zip(df_loaded["Batch ID"], df_loaded["Stack Level"]))
        self.threshold = self.CONFIG['thresholds']['box_model']['confidence_threshold']
        # print(self.threshold)
        self.pallet_status_estimator = PalletStatus()

    def _detect_boxes(self, roi):
        h, w = roi.shape[:2]
        results = self.model(roi, conf=self.threshold, verbose=False)[0]

        boxes = results.boxes.xyxy  # (x1, y1, x2, y2)
        scores = results.boxes.conf  # confidence scores

        # Apply NMS manually
        keep = ops.nms(boxes, scores, iou_threshold=0.5)  # You can change IOU threshold
        boxes = boxes[keep].cpu().numpy()

        return [
            {
                'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                'cx': (x1 + x2) / 2, 'cy': (y1 + y2) / 2
            }
            for x1, y1, x2, y2 in boxes
            if 0 <= x1 < x2 <= w and 0 <= y1 < y2 <= h
        ]

    def _count_stacks(self, box_list):
        if not box_list:
            return 0
        top_sorted = sorted(box_list, key=lambda b: b['cy'])
        top1 = top_sorted[0]
        top2 = top_sorted[1]
        print("len:",len(box_list))
        rx = top1['x2'] - 150
        lx = top1['x1'] + 150
        cy = top1['cy']
        count11 = sum(1 for b in box_list if b['x1'] <= rx <= b['x2'] and b['y1'] >= cy)
        count12 = sum(1 for b in box_list if b['x1'] <= lx <= b['x2'] and b['y1'] >= cy)
        

        rx = top2['x2'] - 150
        lx = top2['x1'] + 150
        cy = top2['cy']
        count21 = sum(1 for b in box_list if b['x1'] <= rx <= b['x2'] and b['y1'] >= cy)
        count22 = sum(1 for b in box_list if b['x1'] <= lx <= b['x2'] and b['y1'] >= cy)



        # for b in box_list:
        #     print(b['x1'], b['x2'])
        print(f"count11: ",count11)
        print(f"count12: ",count12)
        print(f"count21: ",count21)
        print(f"count22: ",count22)
        
        return max(count11, count12, count21, count22) + 1

    def get_status(self,
                   image_path: str,
                   depth_map,
                   boundaries: tuple,
                   dims: tuple,
                   batch_array: list) -> tuple:
    
        left_line_x, right_line_x, upper_line_y, lower_line_y = boundaries

        batch_array = (batch_array + [None, None])[:2]

        left_status, right_status = [
            status if status else "empty"
            for status in self.pallet_status_estimator.get_status(
                image_path, boundaries, dims, depth_map
            )
        ]

        print(f"initial {left_status = }")
        print(f"initial {right_status = }")

        image = cv2.imread(image_path)
        # roi = image[upper_line_y:lower_line_y, left_line_x:right_line_x]
        roi = image
        _, roi_w = roi.shape[:2]
        mid_x = roi_w // 2

        # Detect once on full ROI
        all_boxes = self._detect_boxes(roi)

        temp = []
        for box in all_boxes:
            if left_line_x < box['cx'] < right_line_x and upper_line_y < box['cy'] < lower_line_y:
                temp.append(box)
        all_boxes = temp

        # Split detected boxes by center x
        left_boxes = [box for box in all_boxes if box['cx'] < mid_x]
        right_boxes = [box for box in all_boxes if box['cx'] >= mid_x]

        # Validate left and right separately
        final_left = self._validate_side('left', left_status, batch_array[0],
                                         left_boxes, image, left_line_x, upper_line_y)

        final_right = self._validate_side('right', right_status, batch_array[1],
                                          right_boxes, image, left_line_x + mid_x, upper_line_y)

        return final_left, final_right

    def _validate_side(self, side_name, status, batch_id, box_list, image, offset_x, offset_y):
        print("part number:", batch_id)
        if status == "full" and batch_id in self.REF_DICT:
            expected = self.REF_DICT[batch_id]
            print("Expected count is", expected)
            count = self._count_stacks(box_list)
            print("Stack Count is", count)
            status = "full" if count >= expected else "partial"

        return status
