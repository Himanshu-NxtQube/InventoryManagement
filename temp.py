# import cv2
# import os
# from ultralytics import YOLO

# def predict_and_show_folder(folder_path, model_path, conf_threshold):
#     # Load model
#     model = YOLO(model_path)

#     # Get list of image files
#     image_files = [f for f in os.listdir(folder_path)
#                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]

#     # Sort for consistent order
#     image_files.sort()

#     for image_file in image_files:
#         image_path = os.path.join(folder_path, image_file)
#         print(f"Processing: {image_file}")

#         # Run prediction
#         results = model(image_path)[0]

#         # Load image
#         image = cv2.imread(image_path)

#         # Draw detections
#         for box in results.boxes:
#             conf = float(box.conf)
#             if conf < conf_threshold:
#                 continue

#             cls_id = int(box.cls)
#             label = model.names[cls_id]
#             x1, y1, x2, y2 = map(int, box.xyxy[0])

#             cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
#             cv2.putText(image, f'{label} {conf:.2f}', (x1, y1 - 10),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

#         # Show image and wait for key
#         cv2.imshow("YOLO Prediction", image)
#         print("Press any key for next image or 'q' to quit.")
#         key = cv2.waitKey(0) & 0xFF
#         if key == ord('q'):
#             break

#     cv2.destroyAllWindows()

# # Example usage
# predict_and_show_folder(
#     folder_path='./test images', 
#     model_path='./models/pallet_best_m.pt', 
#     conf_threshold=0.1
# )







from ultralytics import YOLO
import cv2
import numpy as np


class BoundaryDetector:
    def __init__(self, model_path, confidence_threshold=0.5, merge_threshold=20):
        """
        Initializes the model and sets detection thresholds.
        
        Args:
            model_path (str): Path to the YOLO model.
            confidence_threshold (float): Minimum confidence for detection.
            merge_threshold (int): Minimum distance to merge close blue bar centers.
        """
        self.model = YOLO(model_path)
        self.boundary_threshold = confidence_threshold
        self.merge_threshold = merge_threshold

    def get_boundaries(self, image_path):
        """
        Detects blue and orange bars in the image and returns their boundary positions.

        Args:
            image_path (str): Path to the input image.

        Returns:
            Tuple[int, int, int, int]: (left_x, right_x, upper_y, lower_y)
        """
        image = self._load_image(image_path)
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
            if cls == 0:
                center_x = (x1 + x2) // 2
                blue_boxes.append(center_x)
            elif cls == 1:
                orange_boxes.append((y1, y2))

        # Process blue bar: horizontal boundaries (X-axis)
        blue_boxes.sort()
        merged_centers = self._merge_close_centers(blue_boxes, self.merge_threshold)

        if len(merged_centers) == 0:
            left_x = 0
            right_x = img_width - 1
        elif len(merged_centers) == 1:
            center = merged_centers[0]
            if center < img_width // 2:
                left_x = center
                right_x = img_width - 1
            else:
                left_x = 0
                right_x = center
        else:
            left_x = merged_centers[0]
            right_x = merged_centers[-1]

        # Process orange bar: vertical boundaries (Y-axis)
        y_mid = img_height // 2
        upper = [y1 for y1, y2 in orange_boxes if y2 <= y_mid]
        lower = [y2 for y1, y2 in orange_boxes if y1 >= y_mid]

        upper_y = int(min(upper)) if upper else 0
        lower_y = int(max(lower)) if lower else img_height - 1

        return left_x, right_x, upper_y, lower_y

    def _load_image(self, path):
        img = cv2.imread(path)
        if img is None:
            raise ValueError(f"Unable to load image from path: {path}")
        return img

    def _merge_close_centers(self, centers, min_distance):
        merged = []
        for c in centers:
            if not merged or c - merged[-1] > min_distance:
                merged.append(c)
        return merged


def visualize_boundaries(model_path, image_path, confidence_threshold=0.5, merge_threshold=20, save_path=None):
    model = YOLO(model_path)
    image = cv2.imread(image_path)
    # print(model.names)
    # Run detection
    # image = cv2.merge([cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)] * 3)
    results = model.predict(image, verbose=False)[0]
    
    # Draw individual bounding boxes
    for box in results.boxes:
        conf = box.conf.item()
        if conf < confidence_threshold:
            continue
            
        
        cls = int(box.cls.item())
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        
        # Choose color based on class (0=blue, 1=orange)
        color = (255, 0, 0) if cls == 0 else (0, 165, 255)  # Blue for class 0, Orange for class 1
        
        # Draw bounding box
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        
        # Add confidence label
        label = f"{model.names[cls]}: {conf:.2f}"
        print(label)
        cv2.putText(image, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 5, color, 5)

    # Display the result
    cv2.imshow("Detected Boundaries", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Optionally save the image
    if save_path:
        cv2.imwrite(save_path, image)
        print(f"Saved annotated image to {save_path}")


# ============================
# 🔧 Example usage (edit here)
# ============================
if __name__ == "__main__":
    model_path = "./models/box_detection.pt"
    image_path = "./testing images/debug/DJI_0131.JPG"
    confidence = 0.2
    merge_dist = 50
    save_output_path = "output_with_boundaries.jpg"

    visualize_boundaries(model_path, image_path, confidence, merge_dist, save_output_path)

