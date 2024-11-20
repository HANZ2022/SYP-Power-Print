import cv2
import numpy as np
import os


class parameter_adjusting:
    """
    Class to facilitate parameter adjustments, including:
    - Capturing and correcting images
    - Selecting and saving corner points for the Region of Interest
    - Capturing templates for image processing
    """
    
    
    def __init__(self):
        self.parameters_folder = 'parameters'  # Folder to store parameter files and images
        self.points = []  # List to store corner points
        self.frame = None  # Current captured frame
        self.display_frame = None  # Frame displayed for user interaction
        self.shape = ()  # Shape of the corrected image
        
        self.load_points_from_file(f'{self.parameters_folder}/points.txt')
        
        # Ensure the parameter folder exists
        if not os.path.exists(self.parameters_folder):
            os.makedirs(self.parameters_folder)
            
            
            
    def capture_image(self, camera):
        """
        Capture an image from the camera and save it to a file.
        """
        filename = f'{self.parameters_folder}/p1.jpg'
        camera.capture_file(filename)
        print(f'Captured {filename}')
        return cv2.imread(filename)
        
        
    def load_points_from_file(self, file_path):
        """
        Load corner points and image shape from a file.
        """
        self.points.clear()
        self.shape = []
        with open(file_path, 'r') as file:
            for i, line in enumerate(file, 1):
                if i <= 4:
                    x, y = map(int, line.strip().split(','))
                    self.points.append((x, y)) # boundary points of the ROI in the original photo
                elif i == 5:
                    self.shape = list(map(int, line.strip().split(','))) # shape of the calilbrated photo 
                    
                    
    def save_points_to_file(self, file_path):
        """
        Save the selected points and image shape to a file.
        """
        with open(file_path, 'w') as file:
            for point in self.points:
                file.write(f"{point[0]},{point[1]}\n")
            file.write(f"{self.shape[0]},{self.shape[1]},{self.shape[2]}\n")
                    
                    
    def sort_points(self):
        """
        Sort the selected points in a predefined order:
        - Top-left, Top-right, Bottom-left, Bottom-right
        """
        sp = sorted(self.points, key=lambda x: (int(x[1]), int(x[0])))
        if sp[0][0] > sp[1][0]:
            sp[0], sp[1] = sp[1], sp[0]
        if sp[2][0] > sp[3][0]:
            sp[2], sp[3] = sp[3], sp[2]
        return sp

    def imgcorr(self):
        """
        Perform perspective transformation based on the selected corner points.
        this function is used to calibrate the photo to the front view of the region of interest
        """
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
       
               
    def rgb2hex(self, rgb_list):
        """Converts an RGB list to a hexadecimal color code."""
        res = "#"
        for a in rgb_list:
            a_hex = hex(a)
            if a < 16:
                res += "0"
            res += a_hex[2:]
        return res

    def on_EVENT_LBUTTONDOWN(self, event, x, y, flags, param):
        """
        Mouse callback to capture pixel coordinates and display information on the image.
        """
        if event == cv2.EVENT_LBUTTONDOWN and self.frame is not None and (flags & cv2.EVENT_FLAG_CTRLKEY): #when the 'mouse left click' and the 'CTRL' happens
            xy = "%d,%d" % (x, y) # the pixel position the mouse clicked
            rect = (x, y, 10, 10)
            cv2.circle(self.display_frame, (x, y), 1, (255, 155, 0), thickness=-1)
            cv2.putText(self.display_frame, xy, (rect[0] + rect[2], rect[1] + rect[3]), cv2.FONT_HERSHEY_PLAIN,
                        3.0, (0, 0, 0), thickness=3) # print the position clicked (pixel) on the picture 
            print("x:{},y:{}".format(x, y))
            bgr_list = self.frame[y, x]
            rgb_list = bgr_list[::-1]
            print("RGB: ", rgb_list)
            print("hex-color: ", self.rgb2hex(rgb_list))
            print("--" * 20)
            self.points.append((x, y))
            cv2.imshow("video", self.display_frame) #update the photo


    def adjust_corners(self, camera):
        """
        Allow the user to select and adjust corners for perspective transformation.
        """
        end = False
        try:
            while not end:
                capture_more = input("Capture new photo? (1 to capture, 0 to exit): ")
                if capture_more.strip() == '0':
                    # EXit the function
                    end = True
                elif capture_more.strip() == '1':
                    self.frame = self.capture_image(camera)
                    if self.frame is not None:
                        # if the picture was captured successfully
                        self.display_frame = self.frame.copy()
                        print("Ctrl + Left mouse click to select pixels")
                        self.points.clear()
                        
                        # Create a external window for displaying
                        cv2.namedWindow('video', cv2.WINDOW_NORMAL)
                        cv2.setMouseCallback("video", self.on_EVENT_LBUTTONDOWN)

                        end_2 = False
                        while not end_2:
                            # shoe the picture in the created window
                            cv2.imshow("video", self.display_frame)
                            if len(self.points) == 4:
                                dst = self.imgcorr() # Calibrate the picture to the front view
                                cv2.namedWindow('Corrected Image', cv2.WINDOW_NORMAL)
                                cv2.imshow("Corrected Image", dst) # show the calibrated pictuer
                                cv2.imwrite(f'{self.parameters_folder}/output.jpg', dst)
                                self.shape = dst.shape
                                self.save_points_to_file(f'{self.parameters_folder}/points.txt')
                                for i, point in enumerate(self.points):
                                    print(f"Point {i+1}: ({point[0]}, {point[1]})")
                                    
                                cv2.waitKey(0) # wait for user to press any keyboard
                                end_2 = True
                            c = cv2.waitKey(1)
                            if c == 27:  # ESC key to exit
                                end_2 = True

                        cv2.destroyAllWindows() # close all the windows
                    else:
                        print("Failed to capture image.")
                else:
                    print("Invalid input. Please enter 1 to capture or 0 to exit.")
        except KeyboardInterrupt:
            print('Keyboared Interrupt')
            cv2.destroyAllWindows()


    def capture_template(self, camera):
        """
        Capture an image and allow the user to select a template region.
        """
        self.frame = self.capture_image(camera)
        #self.load_points_from_file(f'{self.parameters_folder}/points.txt')
        dst = self.imgcorr()
        cv2.namedWindow('original', cv2.WINDOW_NORMAL)
        cv2.imshow('original', dst)

        end = False
        roi_selected = False
        while not end:
            roi = cv2.selectROI('original', dst, showCrosshair=True, fromCenter=False) # Select the region of interest
            

            if roi != (0, 0, 0, 0):
                x, y, w, h = roi   # the parameter of the ROI
                print(f"Selected ROI: ({x}, {y}), width: {w}, height: {h}")
                dst = dst[y:y + h, x:x + w]
                cv2.imshow('original', dst)
            else:
                print("No ROI selected or invalid selection.")

            print("Press ESC to exit.., press other keys to continue")
            c = cv2.waitKey(0)
            if c == 27: # if the key "ESC" is pressed
                end = True
        cv2.imwrite('template.jpg', dst)
        print("template.jpg saved")
        cv2.destroyAllWindows()

    def adjust_parameters(self, camera):
        """
        Main method to adjust parameters, including:
        - Real size
        - Corner selection
        - Template capture
        """
        end = False
        try:
            while not end:
                # Ask user for the instruction
                mode = input("(1) Adjust real size (2) Adjust corners (3) Capture the template (0) Exit): ")
                if mode == '0':
                    end = True
                elif mode == '1':
                    x = input("Real Length(mm):").strip()
                    y = input("Real Width(mm):").strip()
                    with open(f"{self.parameters_folder}/real_size.txt", 'w') as file:
                        file.write(f"{x},{y}\n")
                elif mode == '2':
                    # To get the boundary of the region of interest
                    self.adjust_corners(camera)
                elif mode == '3':
                    # To get the target logo the sysytem is going to locate 
                    self.capture_template(camera)
                else:
                    print("Invalid input. Please enter 1 to adjust corners, 2 to adjust real size, or 0 to exit.")
        except KeyboardInterrupt:
            # CTRL + C  to interrupt
            print(f"KeyboardInterrupt\n")
