# detect.py
import cv2
import numpy as np
from detect_helper import CameraProcessor, DetectProcessor
from parameters_helper import parameter_adjusting
import os

def change_parameters_folder():
    try:
        files_and_dirs = os.listdir("parameters_support")
        print("The existing parameter folder:")
        for item in files_and_dirs:
            print(item)
    except FileNotFoundError:
        print("Folder 'parameters_support' is missing. Creating a new one...")
        os.makedirs("parameters_support", exist_ok=True)
        print("Folder parameters_support created.")
    parameter_folder = input("Type the folder name to use or create new parameter folder: ")
    os.makedirs(f"parameters_support/{parameter_folder}", exist_ok=True)
    return "parameters_support/" + parameter_folder

# Main entry point of the script
if __name__ == "__main__":
    # Initialize the camera processor to manage camera input
    camera_processor = CameraProcessor()
    camera_processor.start()
    parameter_folder = change_parameters_folder() #Determin the folder will be used to hold the parameters
    
    # Create an instance of parameter_adjusting to manage adjustable parameters
    parameter = parameter_adjusting(parameter_folder)
    
    # Create an instance of DetectProcessor for image detection and processing
    detecter = DetectProcessor()
    try:
        end = False
        while end == False:
            # Display a menu for the user to select a mode
            mode = input("Choose mode: (1) Start Detection (2) Adjust Parameters (3) Modify Camera mode\n(4) Change parameter folder (0) Exit: ")
            if mode == '1':
                # Start the detection process with predefined files and the camera processor
                detecter.process_image(parameter_folder, camera_processor)
                #detecter.process_image(f"parameter_folder/template.jpg", "parameter_folder/points.txt", "parameter_folder/real_size.txt", camera_processor)
            elif mode == '2':
                # Allow the user to adjust parameters for the system
                parameter.adjust_parameters(parameter_folder, camera_processor.camera)
            elif mode == '3':
                # Modify the camera mode (e.g., resolution, settings)
                camera_processor.set_mode()
            elif mode == '4':
                try:
                    parameter_folder = change_parameters_folder()
                except KeyboardInterrupt:
                    print("\nKeyboardInterrupt")
                    
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
