from package.pallet_status import PalletStatus
from ultralytics import YOLO
import torchvision.ops as ops
from package.config_loader import get_config
from package.box_counter import BoxCounter
import pandas as pd
import cv2


class RackStackValidator:
    
    def __init__(self):
        self.CONFIG = get_config()
        self.model = YOLO(self.CONFIG['models']['box_model'])
        self.box_counter = BoxCounter()
        df_loaded = pd.read_csv(self.CONFIG['input']['stack_levels_csv'])

        # Create dictionary with format {Batch ID: Stack Level}
        self.REF_DICT = {
            batch: {"Max Layer": max_layer, "Max Boxes": max_boxes}
            for batch, max_layer, max_boxes in zip(
                df_loaded["Batch"], df_loaded["Max Layer"], df_loaded["Max Boxes"]
            )
        }
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
        top2 = top_sorted[1] if len(top_sorted) > 1 else None
        
        rx = top1['x2'] - 150
        lx = top1['x1'] + 150
        cy = top1['cy']
        count11 = sum(1 for b in box_list if b['x1'] <= rx <= b['x2'] and b['y1'] >= cy)
        count12 = sum(1 for b in box_list if b['x1'] <= lx <= b['x2'] and b['y1'] >= cy)
        
        if top2 == None:
            return max(count11, count12) + 1

        rx = top2['x2'] - 150
        lx = top2['x1'] + 150
        cy = top2['cy']
        count21 = sum(1 for b in box_list if b['x1'] <= rx <= b['x2'] and b['y1'] >= cy)
        count22 = sum(1 for b in box_list if b['x1'] <= lx <= b['x2'] and b['y1'] >= cy)



        # for b in box_list:
        #     print(b['x1'], b['x2'])
        # print(f"count11: ",count11)
        # print(f"count12: ",count12)
        # print(f"count21: ",count21)
        # print(f"count22: ",count22)
        
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

        self.left_stack_count = self._count_stacks(left_boxes)
        self.right_stack_count = self._count_stacks(right_boxes)

        # self.box_counter.estimate_box_count()
        self.left_box_count = self.box_counter.estimate_box_count(self.REF_DICT, batch_array[0], left_status, self.left_stack_count)
        self.right_box_count = self.box_counter.estimate_box_count(self.REF_DICT, batch_array[1], right_status, self.right_stack_count)

        print("left box count:", self.left_box_count)
        print("right box count:", self.right_box_count)

        # Validate left and right separately
        final_left = self._validate_side(left_status, 
                                         batch_array[0],
                                         self.left_stack_count)

        final_right = self._validate_side(right_status, 
                                          batch_array[1],
                                          self.right_stack_count)

        return final_left, final_right
    
    def get_counts(self):
        return (self.left_stack_count, self.right_stack_count), (self.left_box_count, self.right_box_count)

    def _validate_side(self, status, batch_id, count):
        # print("part number:", batch_id)
        if status == "full" and batch_id in self.REF_DICT:
            expected = self.REF_DICT[batch_id]["Max Layer"]
            status = "full" if count >= expected else "partial"

        return status
