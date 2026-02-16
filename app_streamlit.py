import cv2
import streamlit as st
from utils.mapping import load_calibration, pixel_to_robot
from perception.detector import ObjectDetector
import os

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


# Get the directory where app_streamlit.py is located
current_dir = os.path.dirname(__file__)
# Go up one level to the project root, then into 'outputs'
OUTPUT_FOLDER = os.path.join(current_dir, "..", "outputs")
image_path = os.path.join(OUTPUT_FOLDER, "last_capture.jpg")

st.title("MG400 Vision System")

# Sidebar Controls
st.sidebar.header("Settings")
mode = st.sidebar.radio("Operation Mode", ["Plan", "Execute"])
color = st.sidebar.selectbox("Target Color", ["any", "red", "blue", "green"])
confirm_exec = st.sidebar.checkbox("Safety: Confirm Execution")

if st.button("Capture & Detect"):
    img = cv2.imread(image_path)  # Capture logic here
    H = load_calibration()
    detector = ObjectDetector()

    results = detector.find_objects(img, color)

    for obj in results:
        u, v = obj["pixel_center"]
        rx, ry = pixel_to_robot(u, v, H)

        # Annotate image
        cv2.circle(img, (u, v), 10, (0, 255, 0), -1)
        cv2.putText(img, f"X:{rx:.1f} Y:{ry:.1f}", (u+15, v),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    st.image(img, channels="BGR", caption="Processed Scene")

    if mode == "Execute" and confirm_exec:
        st.success(f"Moving robot to {len(results)} targets...")
    elif mode == "Execute" and not confirm_exec:
        st.warning(
            "Execution blocked: Please check 'Confirm Execution' in sidebar.")
