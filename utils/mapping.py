import numpy as np
import json


def load_calibration(filename="calibration.json"):
    with open(filename, 'r') as f:
        data = json.load(f)
    return np.array(data["homography"])


def pixel_to_robot(u, v, H):
    """Transform pixel (u, v) to Robot (X, Y) using Matrix H"""
    p = np.array([u, v, 1.0], dtype=np.float32).reshape(3, 1)
    pr = H @ p
    # Homogeneous divide (Lesson 4, Slide 24)
    X = pr[0, 0] / pr[2, 0]
    Y = pr[1, 0] / pr[2, 0]
    return X, Y
