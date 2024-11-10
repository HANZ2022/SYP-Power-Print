import cv2
import numpy as np
import os

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

    def sort_points(self, points):
        """Sort the points in a specific order."""
        sp = sorted(points, key=lambda x: (int(x[1]), int(x[0])))
        if sp[0][0] > sp[1][0]:
            sp[0], sp[1] = sp[1], sp[0]
        if sp[2][0] > sp[3][0]:
            sp[2], sp[3] = sp[3], sp[2]
        return sp

    def imgcorr(self, src, points):
        """Applies perspective transformation to the image."""
        if len(points) != 4:
            raise ValueError("需要输入四个角点")
        sp = self.sort_points(points)
        width = int(np.sqrt(((sp[0][0] - sp[1][0]) ** 2) + (sp[0][1] - sp[1][1]) ** 2))
        height = int(np.sqrt(((sp[0][0] - sp[2][0]) ** 2) + (sp[0][1] - sp[2][1]) ** 2))
        dstrect = np.array([
            [0, 0],
            [width - 1, 0],
            [0, height - 1],
            [width - 1, height - 1]], dtype="float32")
        transform = cv2.getPerspectiveTransform(np.array(sp, dtype="float32"), dstrect)
        warpedimg = cv2.warpPerspective(src, transform, (width, height))
        return warpedimg

    def save_points_to_file(self, points, file_path):
        """Saves points to a file."""
        with open(file_path, 'w') as file:
            for point in points:
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
                        self.points = []
                        cv2.namedWindow('video', cv2.WINDOW_NORMAL)
                        cv2.setMouseCallback("video", self.on_EVENT_LBUTTONDOWN)
                        
                        end_2 = False                     
                        while end_2 == False:
                            cv2.imshow("video", self.display_frame)
                            if len(self.points) == 4:
                                dst = self.imgcorr(self.frame, self.points)
                                cv2.imshow("Corrected Image", dst)
                                cv2.imwrite(f'{self.parameters_folder}/output.jpg', dst)
                                self.shape = dst.shape
                                self.save_points_to_file(self.points, f'{self.parameters_folder}/points.txt')
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

    def adjust_parameters(self, camera):
        end = False
        try:
            while end == False:
                mode = input("(1) Adjust real size (2) Adjust corners (0) Exit): ")
                if mode == '0':
                    end = True
                elif mode == '1':
                    x = input("Real Length(mm):").strip()
                    y = input("Real Width(mm):").strip()
                    with open(f"{self.parameters_folder}/real_size.txt", 'w') as file:
                        file.write(f"{x},{y}\n")
                elif mode == '2':
                    self.adjust_corners(camera)
                else:
                    print("Invalid input. Please enter 1 to adjust corners, 2 to adjust real size, or 0 to exit.")
                    
        except KeyboardInterrupt:
            print(f"KeyboardInterrupt\n")