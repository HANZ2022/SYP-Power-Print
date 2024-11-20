# detect_helper.py
import time
import cv2
import numpy as np
from picamera2 import Picamera2, Preview
from libcamera import controls
import io


def non_max_suppression(boxes, overlapThresh=0.3):
    """
    Implement non-max suppression to filter overlapping bounding boxes.
    
    This function takes a list of bounding boxes and an overlap threshold as input.
    It returns a list of bounding boxes that are selected based on their overlap with other boxes.
    
    Parameters:
    - boxes: A list of bounding boxes, where each box is represented by a list of four numbers (x1, y1, x2, y2).
    - overlapThresh: A float representing the threshold for overlap. Boxes with overlap greater than this value are suppressed.
    
    Returns:
    - A list of bounding boxes that are selected after applying non-max suppression.
    """
    
    # If no target box found
    if len(boxes) == 0:
        return []
    
    # Convert the list of boxes to a numpy array for easier manipulation
    boxes = np.array(boxes, dtype="float")
    
    # The boxes that are selected
    pick = []
    
    # the coordinates of the boxes
    x1, y1, x2, y2 = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
    
    # the area of each box
    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(y2)
    
    # While there are still indices to process
    while len(idxs) > 0:
        last = len(idxs) - 1
        i = idxs[last]
        
        pick.append(i)
        
        # Calculate the coordinates of the intersection rectangle
        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])
        
        # Calculate the width and height of the intersection rectangle
        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)
        
        # Calculate the overlap between the current box and the other boxes
        overlap = (w * h) / area[idxs[:last]]
        
        # Delete the indices of the boxes that have an overlap greater than the threshold
        idxs = np.delete(idxs, np.concatenate(([last], np.where(overlap > overlapThresh)[0])))
    
    # Return the boxes that were picked after applying non-max suppression
    return boxes[pick].astype("int")


class CameraProcessor:
    def __init__(self):
        """Initialize the camera and set available modes."""
        self.camera = Picamera2()
        self.current_lens_position = 4.75
        self.modes = {
            'high_res': {'size': (4608, 2592), 'framerate': 14.35},
            'medium_res': {'size': (2304, 1296), 'framerate': 56.03},
            'low_res': {'size': (1536, 864), 'framerate': 120.13}
        }
        self.current_mode = 0  # Default mode: high-res

    def start(self):
        """Start the camera with the default configuration."""
        self.set_mode()

    def stop(self):
        """Stop the camera."""
        self.camera.stop()

    def capture_image(self):
        """Capture an image and return it as a numpy array."""
        stream = io.BytesIO()
        self.camera.capture_file(stream, format='jpeg')
        stream.seek(0)
        image = np.frombuffer(stream.read(), dtype=np.uint8)
        return cv2.imdecode(image, cv2.IMREAD_COLOR)

    def configure_camera_mode(self, mode):
        """Configure the camera with the selected mode."""
        if mode < len(self.modes):
            self.current_mode = mode
            mode_config = self.modes[list(self.modes.keys())[mode]]
            
            # Create video configuration
            video_config = self.camera.create_video_configuration(main={
                "size": mode_config['size'],
                "format": "XBGR8888"  # Compatible with OpenCV
            })

            self.stop()
            self.camera.configure(video_config)
            
            # Set the framerate if supported
            try:
                self.camera.set_controls({"FrameDurationLimits": (int(1e6 / mode_config['framerate']), int(1e6 / mode_config['framerate']))})
                print(f"Selected mode: {self.current_mode} successfully")
            except Exception as e:
                print(f"Warning: Unable to set framerate: {e}")

        else:
            raise ValueError("Invalid mode selected")
        print("Camera is restarting, please wait...")
        self.camera.start()
        time.sleep(2)  # Allow the camera to stabilize
        print("Camera is working now")
    def set_mode(self):
        """Allow the user to select a camera mode."""
        print("Available camera modes:")
        for index, m in enumerate(self.modes.keys()):
            print(f"{index}: {m}")

        end = False
        while not end:
            try:
                user_input = input("Please select a camera mode by number: ").strip() # Ask user for the mode
                user_input = int(user_input)
                self.configure_camera_mode(user_input)  # change to the mode chosen 
                end = True
            except ValueError:
                print("Invalid input. Please enter a number corresponding to the mode list.")
            except KeyboardInterrupt:
                print("\nExiting...")
                end = True


class DetectProcessor:
    def __init__(self):
        """Initialize attributes for points, shape, and real size."""
        self.points = []
        self.shape = []
        self.real_size = []

    def load_points_from_file(self, file_path):
        """Load points from a file."""
        with open(file_path, 'r') as file:
            for i, line in enumerate(file, 1):
                if i <= 4:
                    x, y = map(int, line.strip().split(','))
                    self.points.append((x, y))
                elif i == 5:
                    self.shape = list(map(int, line.strip().split(',')))

    def load_real_size_from_file(self, file_path):
        """Load real size information from a file."""
        with open(file_path, 'r') as file:
            first_line = file.readline()
            self.real_size = list(map(int, first_line.strip().split(',')))

    def SortPoint(self):
        """Sort the points to ensure correct ordering for perspective transform."""
        sp = sorted(self.points, key=lambda x: (int(x[1]), int(x[0])))
        if sp[0][0] > sp[1][0]:
            sp[0], sp[1] = sp[1], sp[0]
        if sp[2][0] > sp[3][0]:
            sp[2], sp[3] = sp[3], sp[2]
        return sp

    def imgcorr(self, src):
        """
            Perform perspective transformation on the image.
            Used to calibrate to the front view of the ROI
        """
        sp = self.SortPoint()
        width = int(np.sqrt(((sp[0][0] - sp[1][0]) ** 2) + (sp[0][1] - sp[1][1]) ** 2))
        height = int(np.sqrt(((sp[0][0] - sp[2][0]) ** 2) + (sp[0][1] - sp[2][1]) ** 2))
        dstrect = np.array([
            [0, 0],
            [width - 1, 0],
            [0, height - 1],
            [width - 1, height - 1]], dtype="float32")
        transform = cv2.getPerspectiveTransform(np.array(sp, dtype="float32"), dstrect)
        return cv2.warpPerspective(src, transform, (width, height))

    def process_image(self, path_parameters, camera):
        """Process the image for template matching."""
        
        #Initial the parameters
        template = cv2.imread(f"{path_parameters}/template.jpg")
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        self.points.clear()
        self.shape.clear()
        self.real_size.clear()     
        self.load_points_from_file(f"{path_parameters}/points.txt")
        self.load_real_size_from_file(f"{path_parameters}/real_size.txt")
        
        with open(f'{path_parameters}/{list(camera.modes.keys())[camera.current_mode]}_times.txt', 'w') as file:
            try:
                end = False
                while not end:
                    # Capture an image from the camera
                    start_time = time.time()
                    
                    image = camera.capture_image()
                    print('Captured image to memory')
                    
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    #print(f"Capturing photo time:{elapsed_time} seconds")
                    #file.write(f"{elapsed_time}\n")
                    try:
                        # Perform perspective correction. 
                        warped_image = self.imgcorr(image)
                        target_gray = cv2.cvtColor(warped_image, cv2.COLOR_BGR2GRAY)
                        w, h = template_gray.shape[::-1]
                        res = cv2.matchTemplate(target_gray, template_gray, cv2.TM_CCOEFF_NORMED)
                        threshold = 0.9 #If the matching degree is greater than 0.9, it is considered that the target has been found. 
                        loc = np.where(res >= threshold)
                        boxes = [[pt[0], pt[1], pt[0] + w, pt[1] + h] for pt in zip(*loc[::-1])]
                        boxes = non_max_suppression(boxes) #Reduce the overlap
                        if len(boxes) == 0:   # Boxes has nothig recorded
                            print("Not Found") 
                        display_image = warped_image.copy()
    
                        # Draw bounding boxes and calculate scaled positions
                        for (x1, y1, x2, y2) in boxes:
                            cv2.rectangle(display_image, (x1, y1), (x2, y2), (0, 0, 255), 2)
                            center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
                            cv2.circle(display_image, (center_x, center_y), 5, (255, 0, 0), -1)
                            print(f"Logo: (center_x, center_y) = ({center_x}, {center_y})")
                            scaled_center_x = round(center_x / self.shape[1] * self.real_size[0], 1)
                            scaled_center_y = round(center_y / self.shape[0] * self.real_size[1], 1)
                            print(f"(center_x, center_y) = ({scaled_center_x}, {scaled_center_y})")
                            
                        elapsed_time2 = time.time() - end_time
                        #print(f"Processing image time:{elapsed_time2} seconds")
                        file.write(f"{elapsed_time}\t{elapsed_time2}\n")
                        # Display the processed image
                        cv2.namedWindow('Detected Logo' + self.__class__.__name__, cv2.WINDOW_NORMAL)
                        cv2.imshow('Detected Logo' + self.__class__.__name__, display_image)
                        cv2.waitKey(1)
                    except Exception as e:
                        print(f"Error during image processing: {e}")
    
            except KeyboardInterrupt:
                print("Keyboard Interrupt")
            finally:
                # Clean up display windows
                cv2.destroyAllWindows()
