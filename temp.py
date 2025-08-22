import cv2
import os
import numpy as np
import matplotlib.pyplot as plt

def motion_blur_edge_consistency(image_path, bins=36):
    # Load grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Compute gradients (Sobel)
    gx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)

    # Edge magnitude and orientation
    mag = np.sqrt(gx**2 + gy**2)
    theta = np.arctan2(gy, gx)  # radians (-pi, pi)

    # Keep only strong edges
    mask = mag > np.percentile(mag, 75)
    theta = theta[mask]

    # Histogram of orientations
    hist, edges = np.histogram(theta, bins=bins, range=(-np.pi, np.pi), density=True)

    # Motion blur → one bin much higher than others
    peak = hist.max()
    mean_rest = (hist.sum() - peak) / (len(hist)-1)

    score = peak / (mean_rest + 1e-6)  # anisotropy score

    return score, hist, edges

image_folder = "testing images/debug"
threshold = 100.0
res = []

for filename in os.listdir(image_folder):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
        path = os.path.join(image_folder, filename)
        img = cv2.imread(path)
        # is_blur, score = is_blurry(img, threshold)
        # score = motion_blur_metric(path)
        score, hist, edges = motion_blur_edge_consistency(path)
        # print("Motion blur score:", score)
        res.append((filename, (score, hist, edges)))

res.sort(key=lambda x:x[1][0])
[print(f"{filename} --> {score}") for filename, (score, _,_) in res]

for fn, (score, hist, edges) in res:
    plt.bar((edges[:-1] + edges[1:]) / 2, hist, width=np.pi/18)
    plt.xlabel("Edge orientation (radians)")
    plt.ylabel("Normalized frequency")
    plt.savefig(f"plots/{fn}.png")
# Example usage
# score, hist, edges = motion_blur_edge_consistency("test.jpg")


# Plot histogram (for debugging)

