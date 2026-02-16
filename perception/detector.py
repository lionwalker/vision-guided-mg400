import cv2
import numpy as np
import matplotlib.pyplot as plt


class ObjectDetector:
    def __init__(self):
        # HSV Ranges: [Hue, Saturation, Value]
        # Red often spans two ranges (0-10 and 170-180)
        self.colors = {
            "red": ([0, 150, 50], [10, 255, 255]),
            "blue": ([100, 150, 50], [130, 255, 255]),
            "green": ([40, 100, 50], [80, 255, 255])
        }

    def find_objects(self, image, color_name="any", shape_type="any"):
        # 1. Convert to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # 2. Color Masking
        if color_name in self.colors:
            lower, upper = self.colors[color_name]
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
        else:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

        # 3. Morphology (Cleaning the mask)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # 4. Contour Analysis
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        results = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 500:
                continue  # Filter small noise

            # 5. Circularity (Lesson 5 Shape Descriptor)
            perimeter = cv2.arcLength(cnt, True)
            circularity = (4 * np.pi * area) / \
                (perimeter**2) if perimeter > 0 else 0

            # Label based on Circularity
            detected_shape = "circle" if circularity > 0.8 else "square"

            if shape_type != "any" and detected_shape != shape_type:
                continue

            # Calculate Center (u, v)
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                u = int(M["m10"] / M["m00"])
                v = int(M["m01"] / M["m00"])
                results.append(
                    {"pixel_center": (u, v), "shape": detected_shape, "color": color_name})

        return results
