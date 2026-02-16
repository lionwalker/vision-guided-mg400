import cv2
import os
import argparse
import numpy as np
from perception.detector import ObjectDetector
from utils.mapping import load_calibration, pixel_to_robot
from robot.main import MG400Controller
# from utils.camera import Camera

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")


def run_main():
    # 1. CLI Argument Parsing
    parser = argparse.ArgumentParser(
        description="Dobot Integrated Vision System")
    parser.add_argument(
        "--mode", choices=["plan", "execute"], required=True, help="Mode of operation")
    parser.add_argument("--color", type=str, default="any",
                        help="Filter by color: red, blue, green")
    parser.add_argument("--shape", type=str, default="any",
                        help="Filter by shape: circle, square")
    args = parser.parse_args()

    # Create outputs folder if missing
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 2. Initialization
    try:
        H = load_calibration(os.path.join(BASE_DIR, "calibration.json"))
        print("Success: Calibration loaded.")
    except Exception as e:
        print(f"Error: Could not load calibration. {e}")
        return

    # 3. Capture Image and Read
    # cam = Camera(1)
    # print("Taking photo...")
    # Call the method and store the returned image
    # image = cam.get_frame()
    image_path = os.path.join(OUTPUT_DIR, "camera_detection.jpg")
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: {image_path} not found.")
        return

    # Keep a copy for annotation
    display_img = image.copy()

    # 4. Perception Pipeline
    detector = ObjectDetector()
    found_objs = detector.find_objects(image, args.color, args.shape)

    targets_for_robot = []

    print(f"\n--- RESULTS ({args.mode.upper()} MODE) ---")
    if not found_objs:
        print("No targets found matching criteria.")

    for obj in found_objs:
        u, v = obj["pixel_center"]
        shape_type = obj["shape"]

        # 5. Coordinate Mapping
        rx, ry = pixel_to_robot(u, v, H)
        targets_for_robot.append((rx, ry))

        # 6. Annotation
        cv2.circle(display_img, (u, v), 12, (0, 255, 0), 2)
        text = f"{shape_type} | X:{rx:.1f} Y:{ry:.1f}"
        cv2.putText(display_img, text, (u+15, v-15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        print(
            f"Found {shape_type} at Pixel({u}, {v}) -> Robot({rx:.1f}, {ry:.1f})")

    # 7. Save outputs for UI
    cv2.imwrite(os.path.join(OUTPUT_DIR, "last_detection.png"), display_img)
    print(f"Annotated image saved to outputs/last_detection.png")

    print("targets_for_robot", targets_for_robot)

    # 8. Execution Mode Gate
    if args.mode == "execute" and targets_for_robot:
        bot = MG400Controller()
        for x, y in targets_for_robot:
            bot.pick_and_place(x, y)
    elif args.mode == "execute":
        print("Execution skipped: No targets found.")


if __name__ == "__main__":
    run_main()
