import cv2
import matplotlib.pyplot as plt
import numpy as np
import os

# Get the directory where app_streamlit.py is located
current_dir = os.path.dirname(__file__)
# Go up one level to the project root, then into 'outputs'
OUTPUT_FOLDER = os.path.join(current_dir, "..", "outputs")
image_path = os.path.join(OUTPUT_FOLDER, "camera_detection.png")

img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

_, th = cv2.threshold(img, 110, 255, cv2.THRESH_BINARY_INV)

kernel = np.ones((5, 5), np.uint8)
mask = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)

plt.subplot(1, 2, 1)
plt.imshow(th, cmap='gray')
plt.title("th")
plt.axis('off')
plt.subplot(1, 2, 2)
plt.imshow(mask, cmap='gray')
plt.title("mask")
plt.axis('off')
plt.show()

'''
# Load the original image as grayscale for processing
img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

# Create a 'deep copy' so that drawing operations don't overwrite original_img
original_img = img.copy()

# PREPROCESSING: Improve contrast for real camera images
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
enhanced = clahe.apply(img)

# SMOOTHING: Remove grain/noise (helpful for real tiles)
blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)

# THRESHOLDING: Adaptive thresholding calculates the threshold for small blocks (9x9)
th_binary = cv2.adaptiveThreshold(
    blurred,
    255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY_INV,
    9,
    2
)

# MORPHOLOGY: Clean up small noise and fill holes in tiles
kernel = np.ones((2, 2), np.uint8)
mop = cv2.morphologyEx(th_binary, cv2.MORPH_OPEN,
                       kernel)  # Removes small dots
# Fills holes in objects
mop = cv2.morphologyEx(mop, cv2.MORPH_CLOSE, kernel)

# LABELING
num_labels, labeled_img, stats, centroids = cv2.connectedComponentsWithStats(
    mop)

# ANNOTATION with Area Filtering
annotated = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
# Keep track of where we last drew text to prevent vertical overlap
last_text_x = -100
for i in range(1, num_labels):
    area = stats[i, cv2.CC_STAT_AREA]

    # Only detect objects larger than 100 pixels (ignores noise)
    if area > 100:
        p1x, p1y, w, h, _ = stats[i]
        cv2.rectangle(annotated, (p1x, p1y),
                      (p1x+w, p1y+h), (0, 0, 255), 2)

        # If objects are vertically stacked, move text more to left of the box
        text_x = p1x
        if abs(text_x - last_text_x) < 5:
            text_x = p1x + 100

        cv2.putText(
            annotated,
            f"({p1x},{p1y})",
            (text_x, p1y-10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 41, 9),
            1,
            cv2.LINE_AA
        )

        # Update the tracker for the next loop iteration
        last_text_x = text_x

# Plotting all steps for reporting
titles = ['Grayscaled', 'Enhanced', 'Blurred',
          'Threshbolded', 'Morphologyed', 'Labled', 'Annotated']
plt_images = [original_img, enhanced,
              blurred, th_binary, mop, labeled_img, annotated]
plt.figure(figsize=(12, 10))
for i in range(7):
    plt.subplot(4, 2, i + 1)
    plt.imshow(plt_images[i], cmap='gray')
    plt.title(titles[i])
    plt.axis('off')

# Create the histogram plot
hist_cv = cv2.calcHist([original_img], [0], None, [256], [0, 256])
plt.subplot(4, 2, 8)
plt.title('Histogram')
plt.xlabel('Pixel Intensity')
plt.ylabel('Frequency')
# .plot() is often cleaner than .vlines() for histograms
plt.plot(hist_cv, color='black')
plt.fill_between(range(256), hist_cv.flatten(), color='gray', alpha=0.3)
plt.xlim([0, 256])
plt.show()
'''
