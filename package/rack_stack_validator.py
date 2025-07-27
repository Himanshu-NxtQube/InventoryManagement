from package.pallet_status import PalletStatus
from ultralytics import YOLO
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
        self.pallet_status_estimator = PalletStatus()

    def _detect_boxes(self, roi):
        h, w = roi.shape[:2]
        results = self.model(roi, conf=self.threshold, verbose=False)[0]
        boxes = results.boxes.xyxy.cpu().numpy()
        return [
            {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
             'cx': (x1 + x2) / 2, 'cy': (y1 + y2) / 2}
            for x1, y1, x2, y2 in boxes
            if 0 <= x1 < x2 <= w and 0 <= y1 < y2 <= h
        ]

    def _count_stacks(self, box_list):
        if not box_list:
            return 0
        top = min(box_list, key=lambda b: b['cy'])
        cx, cy = top['cx'], top['cy']
        count = sum(1 for b in box_list if b['x1'] <= cx <= b['x2'] and b['y1'] >= cy)
        # print("Stack:",count+1)
        return count + 1

    def get_status(self,
                   image_path: str,
                   depth_map,
                   boundaries: tuple,
                   dims: tuple,
                   batch_array: list) -> tuple:
    
        left_line_x, right_line_x, upper_line_y, lower_line_y = boundaries

        # Ensure batch_array has 2 elements
        batch_array = (batch_array + [None, None])[:2]

        # Get initial statuses
        left_status, right_status = [
            status if status else "empty"
            for status in self.pallet_status_estimator.get_status(
                image_path, boundaries, dims, depth_map
            )
        ]

        # print(f"initial {left_status = }")
        # print(f"initial {right_status = }")

        image = cv2.imread(image_path)
        roi = image[upper_line_y:lower_line_y, left_line_x:right_line_x]
        _, roi_w = roi.shape[:2]
        mid_x = roi_w // 2

        # Split left and right ROI
        left_roi = roi[:, :mid_x]
        right_roi = roi[:, mid_x:]

        # Detect boxes separately
        left_boxes = self._detect_boxes(left_roi)
        right_boxes = self._detect_boxes(right_roi)

        final_left = self._validate_side('left', left_status, batch_array[0],
                                         left_boxes, image, left_line_x, upper_line_y)

        final_right = self._validate_side('right', right_status, batch_array[1],
                                          right_boxes, image, left_line_x + mid_x, upper_line_y)

        # cv2.imshow("Rack Stack Verification", image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        return final_left, final_right

    def _validate_side(self, side_name, status, batch_id, box_list, image, offset_x, offset_y):
        # print("REACHED HERE!")
        print("part number:",batch_id)
        if status == "full" and batch_id in self.REF_DICT:
            expected = self.REF_DICT[batch_id]
            print("Expected count is", expected)
            count = self._count_stacks(box_list)
            print("Stack Count is", count)
            status = "full" if count >= expected else "partial"
        # Draw boxes regardless of status
        #self._draw_visual(image, box_list, offset_x, offset_y, side_name)
        return status

    # def _draw_visual(self, image, boxes, offset_x, offset_y, side):
    #     if not boxes:
    #         print(f"[INFO] No boxes on {side}")
    #         return

    #     top = min(boxes, key=lambda b: b['cy'])
    #     cx, cy = int(top['cx'] + offset_x), int(top['cy'] + offset_y)

    #     counted, others = [], []
    #     for b in boxes:
    #         gx1, gy1 = int(b['x1'] + offset_x), int(b['y1'] + offset_y)
    #         gx2, gy2 = int(b['x2'] + offset_x), int(b['y2'] + offset_y)
    #         if b['x1'] <= (cx - offset_x) <= b['x2'] and b['y1'] >= (cy - offset_y):
    #             counted.append((gx1, gy1, gx2, gy2))
    #         else:
    #             others.append((gx1, gy1, gx2, gy2))

    #     for x1, y1, x2, y2 in counted:
    #         cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    #     for x1, y1, x2, y2 in others:
    #         cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)

    #     cv2.line(image, (cx, cy), (cx, image.shape[0]), (255, 0, 0), 2)
    #     cv2.circle(image, (cx, cy), 5, (255, 255, 0), -1)

    #     count = len(counted) + 1
    #     y_text = 30 if side == 'left' else 60
    #     cv2.putText(image, f"{side} count: {count}", (30, y_text),
    #                 cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)


if __name__=="__main__":
    rack_stack = RackStackValidator()
    rack_stack.get_status('./test images/DJI_0135.JPG')