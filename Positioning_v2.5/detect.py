# detect.py
import cv2
import numpy as np
from detect_helper import CameraProcessor, DetectProcessor
from parameters_helper import parameter_adjusting


if __name__ == "__main__":
    camera_processor = CameraProcessor()
    camera_processor.start()
    
    # 创建 CameraCalibrator 实例
    parameter = parameter_adjusting()
    detecter = DetectProcessor()
    try:
        end = False
        while end == False:
            mode = input("Choose mode: (1) Start Detection (2) Adjust Parameters (0) Exit: ")
            if mode == '1':
                detecter.process_image("template1.jpg","parameters/points.txt","parameters/real_size.txt",camera_processor)
            elif mode == '2':
                parameter.adjust_parameters(camera_processor.camera)
            elif mode == '0':
                print("Exiting program...")
                end = True
            else:
                print("Invalid input. Please enter 1 to start detection, 2 to adjust parameters, or 0 to exit.")
    except KeyboardInterrupt:
        print("\nProgram interrupted, exiting...")