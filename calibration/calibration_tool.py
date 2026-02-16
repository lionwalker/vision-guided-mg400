import cv2
import numpy as np
import json
import os

# Storage for clicked points
img_pts = []


def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        img_pts.append([x, y])
        print(f"Captured Pixel: {x}, {y}")


def run_calibration():

    # Get the directory where app_streamlit.py is located
    current_dir = os.path.dirname(__file__)
    # Go up one level to the project root, then into 'outputs'
    OUTPUT_FOLDER = os.path.join(current_dir, "..", "outputs")
    image_path = os.path.join(OUTPUT_FOLDER, "last_capture.jpg")

    # 1. Setup
    image = cv2.imread(image_path)  # Or capture live
    cv2.imshow("Calibration - Click 4 Points", image)
    cv2.setMouseCallback("Calibration - Click 4 Points", mouse_callback)

    print("Click 4 points on the image, then press any key.")
    cv2.waitKey(0)

    if len(img_pts) < 4:
        print("Error: Need at least 4 points!")
        return

    # 2. Input Robot coordinates for those 4 points
    robot_pts = []
    for i in range(len(img_pts)):
        print(f"For Pixel Point {img_pts[i]}...")
        rx = float(input("Enter Robot X: "))
        ry = float(input("Enter Robot Y: "))
        robot_pts.append([rx, ry])

    # 3. Compute H (Lesson 4)
    H, _ = cv2.findHomography(np.array(img_pts), np.array(robot_pts))

    # 4. Save to JSON (This is the crucial step for the Final Project)
    calib_data = {
        "homography": H.tolist(),
        "notes": "Lab 5 Integrated System Calibration",
        "image_size": [image.shape[1], image.shape[0]]
    }

    # Save to project root so main.py can find it
    with open("calibration.json", "w") as f:
        json.dump(calib_data, f)
    print("Calibration saved successfully to calibration.json")


if __name__ == "__main__":
    run_calibration()
