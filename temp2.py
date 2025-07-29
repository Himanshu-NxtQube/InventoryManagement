import cv2
import numpy as np
from ultralytics import YOLO

def draw_boxes_with_rx_line(image_path, box_list):
    image = cv2.imread(image_path)
    if image is None:
        print("Failed to load image.")
        return

    h, w = image.shape[:2]
    
    if not box_list:
        print("No boxes to draw.")
        return

    # Identify top box (minimum cy)
    top_box = min(box_list, key=lambda b: b['cy'])
    rx = top_box['x2'] - 115
    cy = top_box['cy']

    counted_boxes = []
    other_boxes = []

    for b in box_list:
        if b['x1'] <= rx <= b['x2'] and b['y1'] >= cy:
            counted_boxes.append(b)
        else:
            other_boxes.append(b)

    # Draw vertical line from (rx, cy) to bottom of image
    cv2.line(image, (int(rx), int(cy)), (int(rx), h), (255, 255, 0), 2)

    # Draw counted boxes (green)
    for b in counted_boxes:
        x1, y1, x2, y2 = map(int, [b['x1'], b['y1'], b['x2'], b['y2']])
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Draw other boxes (red)
    for b in other_boxes:
        x1, y1, x2, y2 = map(int, [b['x1'], b['y1'], b['x2'], b['y2']])
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)

    # Optional text overlay
    cv2.putText(image, f"Counted: {len(counted_boxes) + 1}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    # cv2.imshow("Stack Validation", image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    cv2.imwrite("output_with_boundaries.png", image)

def _detect_boxes(roi):
        h, w = roi.shape[:2]
        model = YOLO('./models/Marico Box Detection.pt')
        results = model(roi, conf=.5, verbose=False)[0]
        boxes = results.boxes.xyxy.cpu().numpy()
        return [
            {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
             'cx': (x1 + x2) / 2, 'cy': (y1 + y2) / 2}
            for x1, y1, x2, y2 in boxes
            if 0 <= x1 < x2 <= w and 0 <= y1 < y2 <= h
        ]


# Example usage:
if __name__ == "__main__":
    # Replace with actual boxes from YOLO output
    image_path = "/run/media/cyrenix/Productive Things/Work/Marico Inventory code/images/new_testing2/DJI_0495.JPG"
    image = cv2.imread(image_path)
    h, w, _ = image.shape
    image = image[:, :w//2]
    res = _detect_boxes(image)
    draw_boxes_with_rx_line(image_path, res)
