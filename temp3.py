import cv2
import io
from google.cloud import vision
from google.cloud.vision_v1 import types
import os

# Set up credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./models/GoogleVisionCredential.json"

# Initialize client
client = vision.ImageAnnotatorClient()

# Load image
image_path = "./testing images/debug/DJI_0547.JPG"
with io.open(image_path, 'rb') as image_file:
    content = image_file.read()
# image = cv2.imread(image_path)
# _, image_encoded = cv2.imencode('.jpg', image)
# content = image_encoded.tobytes()

image = vision.Image(content=content)

# Perform OCR
response = client.text_detection(image=image)
texts = response.text_annotations

# Load image using OpenCV
img = cv2.imread(image_path)

# Draw bounding boxes and annotations
for i, text in enumerate(texts):
    vertices = [(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices]
    pts = vertices + [vertices[0]]  # close the loop
    for j in range(len(pts) - 1):
        cv2.line(img, pts[j], pts[j + 1], (0, 255, 0) if i == 0 else (255, 0, 0), 2)

    if i > 0:  # first one is the entire text block, skip it
        x, y = pts[0]
        cv2.putText(img, text.description, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
cv2.line(img, (0, 2570), (4032, 2570), (0,0, 255), 5)
# Show image
# cv2.imshow("OCR Annotations", img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
cv2.imwrite("annotations.png", img)