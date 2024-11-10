# detect.py
import cv2
import numpy as np
from detect_helper import CameraProcessor, load_calibration_params, load_points_from_file, imgcorr, non_max_suppression, load_real_size_from_file
from view_calibration_helper import CameraCalibrator

def process_image(image, template, template_gray, intrinsic_matrix, distortion_coeffs, points, real_size, shape):
    """Process the image and perform template matching."""
    try:
        warped_image = imgcorr(image, points)
        target_gray = cv2.cvtColor(warped_image, cv2.COLOR_BGR2GRAY)
        w, h = template_gray.shape[::-1]
        res = cv2.matchTemplate(target_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        threshold = 0.9
        loc = np.where(res >= threshold)
        boxes = [[pt[0], pt[1], pt[0] + w, pt[1] + h] for pt in zip(*loc[::-1])]
        boxes = non_max_suppression(boxes)
        
        display_image = warped_image.copy()
        for (x1, y1, x2, y2) in boxes:
            cv2.rectangle(display_image, (x1, y1), (x2, y2), (0, 0, 255), 2)
            center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
            cv2.circle(display_image, (center_x, center_y), 5, (255, 0, 0), -1)
            print(f"Logo: (center_x, center_y) = ({center_x}, {center_y})")
            scaled_center_x = round(center_x / shape[1] * real_size[0], 1)
            scaled_center_y = round(center_y / shape[0] * real_size[1], 1)
            print(f"(center_x, center_y) = ({scaled_center_x}, {scaled_center_y})")
        #resized_img = cv2.resize(display_image, (1920, 1080))
        #cv2.imshow('Detected Logo', resized_img)
        cv2.namedWindow('Detected Logo', cv2.WINDOW_NORMAL)
        cv2.imshow('Detected Logo', display_image)
        cv2.waitKey(30)
    except Exception as e:
        print(f"Error during image processing: {e}")

if __name__ == "__main__":
    camera_processor = CameraProcessor()
    camera_processor.start()
    
    # 创建 CameraCalibrator 实例
    calibrator = CameraCalibrator()
    
    try:
        while True:
            mode = input("Choose mode: (1) Start Detection (2) Adjust Parameters (0) Exit: ")
            if mode == '1':
                intrinsic_matrix, distortion_coeffs = load_calibration_params()
                template = cv2.imread('template.jpg')
                template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
                points, shape = load_points_from_file('corner/points.txt')
                real_size = load_real_size_from_file('corner/real_size.txt')
                try:
                    while True:
                        image = camera_processor.capture_image()
                        print('Captured image to memory')
                        process_image(image, template, template_gray, intrinsic_matrix, distortion_coeffs, points, real_size, shape)
                except KeyboardInterrupt:
                    print("程序中断，退出...")
                finally:
                    # camera_processor.stop()  # 注释掉了此行，如需停止相机请去掉注释
                    cv2.destroyAllWindows()
            elif mode == '2':
                calibrator.adjust_parameters(camera_processor.camera)
            elif mode == '0':
                print("Exiting program...")
                break
            else:
                print("Invalid input. Please enter 1 to start detection, 2 to adjust parameters, or 0 to exit.")
    except KeyboardInterrupt:
        print("\n程序中断，退出...")