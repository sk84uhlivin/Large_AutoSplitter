import cv2
from cv2_enumerate_cameras import enumerate_cameras
import keyboard
import time
import tkinter as tk
from tkinter import ttk


def is_color_within_tolerance(detected_color, target_color, tolerance):
    """
    Check if the detected color is within a specified tolerance of the target color.

    Args:
        detected_color (tuple): The detected (R, G, B) color.
        target_color (tuple): The target (R, G, B) color.
        tolerance (int): The allowable deviation for each color channel.

    Returns:
        bool: True if within tolerance, False otherwise.
    """
    return all(abs(detected_color[i] - target_color[i]) <= tolerance for i in range(3))


def monitor_pixels_and_send_key(
        pixel_coords_1, target_color_1, tolerance_1,
        pixel_coords_2, target_color_2, tolerance_2,
        key_to_press, webcam_index):
    """
    Monitor two pixel coordinates for specific color conditions and send a keystroke when conditions are met.

    Args:
        pixel_coords_1 (tuple): The coordinates of the first pixel to monitor (x, y).
        target_color_1 (tuple): The target (R, G, B) color for the first pixel.
        tolerance_1 (int): Tolerance for the first pixel's color check.
        pixel_coords_2 (tuple): The coordinates of the second pixel to monitor (x, y).
        target_color_2 (tuple): The target (R, G, B) color for the second pixel.
        tolerance_2 (int): Tolerance for the second pixel's color check.
        key_to_press (str): The keystroke to send when conditions are met.
        webcam_index (int): The webcam index to use.
    """
    cap = cv2.VideoCapture(webcam_index)
    if not cap.isOpened():
        print(f"Error: Could not open webcam with index {webcam_index}.")
        return

    # Force max resolution (e.g., 1920x1080). Modify as needed.
    desired_width, desired_height = 1920, 1080
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, desired_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, desired_height)

    # Get the actual resolution
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Actual Webcam Resolution: {width}x{height}")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame from webcam.")
                break

            # Get the colors at the specified pixel coordinates
            color_1 = tuple(int(value) for value in frame[pixel_coords_1[1], pixel_coords_1[0]][::-1])
            color_2 = tuple(int(value) for value in frame[pixel_coords_2[1], pixel_coords_2[0]][::-1])

            # print(f"Detected color at {pixel_coords_1}: {color_1}")
            # print(f"Detected color at {pixel_coords_2}: {color_2}")

            # Check conditions
            condition_1 = not is_color_within_tolerance(color_1, target_color_1, tolerance_1)
            condition_2 = is_color_within_tolerance(color_2, target_color_2, tolerance_2)

            if condition_1 and condition_2:
                keyboard.press_and_release(key_to_press)

                print(
                    f"Conditions met! Target 1: {target_color_1}, Detected 1: {color_1} "
                    f"OUTSIDE tolerance {tolerance_1}. "
                    f"Target 2: {target_color_2}, Detected 2: {color_2} "
                    f"WITHIN tolerance {tolerance_2}. Sending keystroke '{key_to_press}'."
                )

                # Sleep for 30 seconds
                time.sleep(30)

                # Flush the buffer by reading/disposing a few frames after sleep
                for _ in range(5):
                    cap.read()

    finally:
        cap.release()
        cv2.destroyAllWindows()


def select_webcam():
    def on_select():
        # Extract camera index from menu selection
        selected_camera = webcam_combobox.get()  # String
        selected_index = selected_camera.split(":")[0].strip()
        selected_index = int(selected_index)

        root.destroy()

        # Define parameters for monitoring
        pixel_coords_1 = (1409, 83)  # First pixel coordinates
        target_color_1 = (239, 225, 25)  # First target color
        tolerance_1 = 50  # First tolerance

        pixel_coords_2 = (979, 114)  # Second pixel coordinates
        target_color_2 = (195, 152, 217)  # Second target color
        tolerance_2 = 23  # Second tolerance

        key_to_press = 'F8'  # Keystroke to send

        monitor_pixels_and_send_key(
            pixel_coords_1, target_color_1, tolerance_1,
            pixel_coords_2, target_color_2, tolerance_2,
            key_to_press, webcam_index=selected_index
        )

    root = tk.Tk()
    root.title("Select Webcam")

    tk.Label(root, text="Select Webcam:").pack(pady=5)

    webcam_indices = []
    for camera_info in enumerate_cameras():
        camera_profile = f'{camera_info.index}: {camera_info.name}'
        print(camera_profile)
        webcam_indices.append(camera_profile)

    if not webcam_indices:
        tk.Label(root, text="No webcams detected.").pack(pady=5)
        root.mainloop()
        return

    webcam_combobox = ttk.Combobox(root, values=webcam_indices, state="readonly")
    webcam_combobox.set(webcam_indices[0])
    webcam_combobox.pack(pady=5)

    select_button = tk.Button(root, text="Select", command=on_select)
    select_button.pack(pady=10)

    root.mainloop()


# Start the program by allowing webcam selection
select_webcam()
