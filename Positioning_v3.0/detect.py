# detect.py
import cv2
import numpy as np
from detect_helper import CameraProcessor, DetectProcessor
from parameters_helper import parameter_adjusting

# Main entry point of the script
if __name__ == "__main__":
    # Initialize the camera processor to manage camera input
    camera_processor = CameraProcessor()
    camera_processor.start()
    
    # Create an instance of parameter_adjusting to manage adjustable parameters
    parameter = parameter_adjusting()
    
    # Create an instance of DetectProcessor for image detection and processing
    detecter = DetectProcessor()
    try:
        end = False
        while end == False:
            # Display a menu for the user to select a mode
            mode = input("Choose mode: (1) Start Detection (2) Adjust Parameters (3) Modify Camera mode (0) Exit: ")
            if mode == '1':
                # Start the detection process with predefined files and the camera processor
                detecter.process_image("template.jpg", "parameters/points.txt", "parameters/real_size.txt", camera_processor)
            elif mode == '2':
                # Allow the user to adjust parameters for the system
                parameter.adjust_parameters(camera_processor.camera)
            elif mode == '3':
                # Modify the camera mode (e.g., resolution, settings)
                camera_processor.set_mode()
            elif mode == '0':
                # Exit the program
                print("Exiting program...")
                end = True
            else:
                # Handle invalid input by prompting the user again
                print("Invalid input. Please enter 1 to start detection, 2 to adjust parameters, or 0 to exit.")
    except KeyboardInterrupt:
        # Handle program interruption (Ctrl+C) gracefully
        print("\nProgram interrupted, exiting...")
