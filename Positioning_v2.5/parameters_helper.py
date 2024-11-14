import cv2
import numpy as np
import os

# 全局变量，用于跟踪Ctrl键的状态
ctrl_pressed = False

def on_key(event, x, y, flags, param):
    global ctrl_pressed
    if event == cv2.EVENT_KEYDOWN:
        if ord('c') == cv2.waitKey(1) & 0xFF:  # 检测C键是否被按下
            ctrl_pressed = True
    elif event == cv2.EVENT_KEYUP:
        if ord('c') == cv2.waitKey(1) & 0xFF:  # 检测C键是否被释放
            ctrl_pressed = False


class parameter_adjusting:
    def __init__(self):
        self.parameters_folder = 'parameters'
        self.points = []
        self.frame = None
        self.display_frame = None
        self.shape = ()

        # Ensure the corner folder exists
        if not os.path.exists(self.parameters_folder):
            os.makedirs(self.parameters_folder)

    def rgb2hex(self, rgb_list):
        """Converts an RGB list to a hexadecimal color code."""
        res = "#"
        for a in rgb_list:
            a_hex = hex(a)
            if a < 16:
                res += "0"
            res += a_hex[2:]
        return res

    def sort_points(self):
        """Sort the points in a specific order."""
        sp = sorted(self.points, key=lambda x: (int(x[1]), int(x[0])))
        if sp[0][0] > sp[1][0]:
            sp[0], sp[1] = sp[1], sp[0]
        if sp[2][0] > sp[3][0]:
            sp[2], sp[3] = sp[3], sp[2]
        return sp

    def imgcorr(self):
        """Applies perspective transformation to the image."""
        if len(self.points) != 4:
            raise ValueError("Four corners are required")
        sp = self.sort_points()
        width = int(np.sqrt(((sp[0][0] - sp[1][0]) ** 2) + (sp[0][1] - sp[1][1]) ** 2))
        height = int(np.sqrt(((sp[0][0] - sp[2][0]) ** 2) + (sp[0][1] - sp[2][1]) ** 2))
        dstrect = np.array([
            [0, 0],
            [width - 1, 0],
            [0, height - 1],
            [width - 1, height - 1]], dtype="float32")
        transform = cv2.getPerspectiveTransform(np.array(sp, dtype="float32"), dstrect)
        warpedimg = cv2.warpPerspective(self.frame, transform, (width, height))
        return warpedimg

    def save_points_to_file(self, file_path):
        """Saves points to a file."""
        with open(file_path, 'w') as file:
            for point in self.points:
                file.write(f"{point[0]},{point[1]}\n")
            file.write(f"{self.shape[0]},{self.shape[1]},{self.shape[2]}\n")

    def on_EVENT_LBUTTONDOWN(self, event, x, y, flags, param):
        """Mouse callback function to get pixel color information."""
        # Check if the left mouse button is pressed and the Ctrl key is also pressed
        if event == cv2.EVENT_LBUTTONDOWN and self.frame is not None and (flags & cv2.EVENT_FLAG_CTRLKEY):
            xy = "%d,%d" % (x, y)
            rect = (x, y, 10, 10)            
            cv2.circle(self.display_frame, (x, y), 1, (255, 155, 0), thickness=-1)
            cv2.putText(self.display_frame, xy, (rect[0]+rect[2], rect[1]+rect[3]), cv2.FONT_HERSHEY_PLAIN,
                        3.0, (0,0,0), thickness=3)
            print("x:{},y:{}".format(x, y))
            bgr_list = self.frame[y, x]
            rgb_list = bgr_list[::-1]
            print("RGB: ", rgb_list)
            print("hex-color: ", self.rgb2hex(rgb_list))
            print("--" * 20)
            self.points.append((x, y))
            cv2.imshow("video", self.display_frame)

    def capture_image(self, camera):
        """Captures an image using the camera."""
        filename = f'{self.parameters_folder}/p1.jpg'
        camera.capture_file(filename)
        print(f'Captured {filename}')
        return cv2.imread(filename)

    def adjust_corners(self, camera):
        """Allows user to adjust parameters by capturing and correcting images."""
        end = False
        try:
            while end == False:
                capture_more = input("Capture new photo? (1 to capture, 0 to exit): ")
                if capture_more.strip() == '0':
                    end = True
                elif capture_more.strip() == '1':
                    self.frame = self.capture_image(camera)
                    if self.frame is not None:
                        self.display_frame = self.frame.copy()                    
                        print("Ctrl + Left mouse click to select pixels")
                        self.points.clear()
                        cv2.namedWindow('video', cv2.WINDOW_NORMAL)
                        cv2.setMouseCallback("video", self.on_EVENT_LBUTTONDOWN)
                        
                        end_2 = False                     
                        while end_2 == False:
                            cv2.imshow("video", self.display_frame)
                            if len(self.points) == 4:
                                dst = self.imgcorr()
                                cv2.imshow("Corrected Image", dst)
                                cv2.imwrite(f'{self.parameters_folder}/output.jpg', dst)
                                self.shape = dst.shape
                                self.save_points_to_file(f'{self.parameters_folder}/points.txt')
                                for i, point in enumerate(self.points):
                                    print(f"Point {i+1}: ({point[0]}, {point[1]})")
                                cv2.waitKey(0)
                                end_2 = True
                            c = cv2.waitKey(1)
                            if c == 27:  # ESC key to exit
                                end_2 = True

                        cv2.destroyAllWindows()
                    else:
                        print("Failed to capture image.")
                else:
                    print("Invalid input. Please enter 1 to capture or 0 to exit.")
        except KeyboardInterrupt:
            print('Camera stopped.')
            cv2.destroyAllWindows()
            
    def load_points_from_file(self, file_path):
        self.points.clear()
        self.shape = []
        with open(file_path, 'r') as file:
            for i, line in enumerate(file, 1):
                if i <= 4:
                    x, y = map(int, line.strip().split(','))
                    self.points.append((x, y))
                elif i == 5:
                    self.shape = list(map(int, line.strip().split(','))) 


    def capture_template(self, camera):
        self.frame = self.capture_image(camera) 
        self.load_points_from_file(f'{self.parameters_folder}/points.txt')
        dst = self.imgcorr()            
        # 显示图像
        cv2.namedWindow('original', cv2.WINDOW_NORMAL)
        cv2.imshow('original', dst)
        
        # 循环直到用户按下'q'键
        end = False
        while not end:
            # 选择ROI
            roi = cv2.selectROI('original', dst, showCrosshair=True, fromCenter=False)
            x, y, w, h = roi
            print(f"Selected ROI: ({x}, {y}, {w}, {h})")

            # 检查ROI是否有效
            if roi != (0, 0, 0, 0):
                # 更新dst为用户选择的ROI区域
                dst = dst[y:y+h, x:x+w]
                
                # 显示新的dst图像
                cv2.imshow('original', dst)
                
                # 保存新的dst图像
                #cv2.imwrite('cropped_image.jpg', cropped_dst)
                #print('Saved!')
            else:
                print("No ROI selected or invalid selection.")

            print("Press ESC to exit.., press other keys to continue")
            c = cv2.waitKey(0)
            if c == 27:  # 按'q'键退出循环
                end = True
        cv2.imwrite('template.jpg', dst)
        print("template.jpg saved")
        # 退出
        cv2.destroyAllWindows()

       
    def adjust_parameters(self, camera):
        end = False
        try:
            while end == False:
                mode = input("(1) Adjust real size (2) Adjust corners (3) Capture the template (0) Exit): ")
                if mode == '0':
                    end = True
                elif mode == '1':
                    x = input("Real Length(mm):").strip()
                    y = input("Real Width(mm):").strip()
                    with open(f"{self.parameters_folder}/real_size.txt", 'w') as file:
                        file.write(f"{x},{y}\n")
                elif mode == '2':
                    self.adjust_corners(camera)
                elif mode == '3':
                    self.capture_template(camera)
                else:
                    print("Invalid input. Please enter 1 to adjust corners, 2 to adjust real size, or 0 to exit.")
                    
        except KeyboardInterrupt:
            print(f"KeyboardInterrupt\n")