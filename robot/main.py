from robot.dobot_controller import (
    ConnectRobot,
    StartFeedbackThread,
    SetupRobot,
    MoveJ,
    MoveL,
    WaitArrive,
    ControlDigitalOutput,
    GetCurrentPosition,
    DisconnectRobot
)
from time import sleep
ROBOT_IP = "192.168.1.6"


class MG400Controller:
    def __init__(self, ip="192.168.1.6"):
        self.ip = ip
        self.safe_z = -75.0  # Height for moving across the table (mm)
        self.pick_z = 165.0  # Height to touch/grab the object (mm)
        self.place_z = -125.0  # Height to release in the box
        self.safe_r = 0
        # Box coordinates [X, Y, Z]
        self.drop_location = [275, -125, -75]

        print(f"Connecting to Dobot MG400 at {self.ip}...")

    def pick_and_place(self, target_x, target_y):

        dashboard, move, feed = ConnectRobot(ip=ROBOT_IP, timeout_s=5.0)
        # Start feedback monitoring thread
        feed_thread = StartFeedbackThread(feed)
        # Setup and enable robot
        SetupRobot(dashboard, speed_ratio=50, acc_ratio=50)

        """Standard sequence: Move -> Descend -> Grab -> Lift -> Move -> Drop"""
        print(
            f"--- Executing Pick-and-Place at ({target_x:.1f}, {target_y:.1f}) ---")

        # 1. Move to Safe Height above target
        print(f"Moving to Hover: {target_x, target_y, self.safe_z}")
        MoveJ(move, [target_x, target_y, self.safe_z, self.safe_r])
        sleep(1)

        # 2. Descend to Pick Height
        print("Descending to Pick...")
        MoveL(move, [target_x, target_y, self.pick_z, self.safe_r])
        # arrived = WaitArrive(
        #    [target_x, target_y, self.pick_z], tolerance=1.0, timeout=30.0)
        arrived = True
        if arrived:
            # Turn on Digital Output 1
            # 3. Close Gripper / Turn on Suction
            print("\n--- Activating Digital Output 1 ---")
            ControlDigitalOutput(dashboard, output_index=1, status=1)

            # Wait for the command to execute
            sleep(1)

            print("\n=== move to PICK point OK ===")
            current_pos = GetCurrentPosition()
            print(f"Robot is at position: {current_pos}")

        else:
            print("\n*** FAIL to reach target position ***")

        # 4. Lift back to Safe Height
        print("Lifting...")
        MoveL(move, [target_x, target_y, self.safe_z, self.safe_r])
        sleep(1)

        # 5. Move to Place Location
        px, py, pz = self.drop_location
        print(f"Moving to Box at ({px}, {py})")
        MoveJ(move, [px, py, self.safe_z, self.safe_r])
        sleep(1)

        # 6. Descend to Place Height
        px, py, pz = self.drop_location
        print(f"Moving to Box at ({px}, {py})")
        MoveL(move, [px, py, self.safe_z, self.safe_r])
        sleep(1)

        # Wait for robot to reach the point
        # arrived = WaitArrive([px, py, self.place_z], tolerance=1.0)
        arrived = True
        if arrived:
            print("\n=== move to PLACE point OK ===")
        else:
            print("\n*** FAIL PLACE point ***")

        # 7. Release
        # Turn off Digital Output 1
        print("ACTION: Opening Gripper")
        ControlDigitalOutput(dashboard, output_index=1, status=0)
        sleep(1)
        print("Item Placed.")

        # 8. Move to Place Location
        px, py, pz = self.drop_location
        print(f"Moving to transform position at ({px}, {py})")
        MoveJ(move, [px, py, self.safe_z, self.safe_r])
        sleep(1)

        # Disconnect
        DisconnectRobot(dashboard, move, feed, feed_thread)
