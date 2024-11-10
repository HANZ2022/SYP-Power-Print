# detect_helper.py
import time
import cv2
import numpy as np
from picamera2 import Picamera2, Preview
from libcamera import controls
import io

class CameraProcessor:
    def __init__(self):
        """Initialize the camera and configure settings."""
        self.camera = Picamera2()
        self.camera_config = self.camera.create_still_configuration()
        self.camera.configure(self.camera_config)
        self.current_lens_position = 4.75

    def start(self):
        """Start the camera with pre-defined settings."""
        self.camera.start()
        time.sleep(2)  # ???????
        '''
        self.camera.set_controls({
            "AfMode": controls.AfModeEnum.Manual,
            "LensPosition": self.current_lens_position,
            "ExposureTime": 5000,
            "AnalogueGain": 1.0
        })
        '''
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

def load_calibration_params():
    """Load intrinsic matrix and distortion coefficients from file."""
    with open('calibration_results.txt', 'r') as f:
        lines = f.readlines()
    intrinsic_matrix = np.array([[float(val) for val in lines[1].split()],
                                 [float(val) for val in lines[2].split()],
                                 [float(val) for val in lines[3].split()]])
    distortion_coeffs = np.array([float(val) for val in lines[6:11]])
    return intrinsic_matrix, distortion_coeffs

def undistort_image(image, intrinsic_matrix, distortion_coeffs):
    """Correct image distortion."""
    h, w = image.shape[:2]
    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(intrinsic_matrix, distortion_coeffs, (w, h), 1, (w, h))
    undistorted_image = cv2.undistort(image, intrinsic_matrix, distortion_coeffs, None, new_camera_matrix)
    x, y, w, h = roi
    if w > 0 and h > 0:
        undistorted_image = undistorted_image[y:y+h, x:x+w]
    return undistorted_image

def non_max_suppression(boxes, overlapThresh=0.3):
    """Implement non-max suppression to filter redundant boxes."""
    if len(boxes) == 0:
        return []
    boxes = np.array(boxes, dtype="float")
    pick = []
    x1, y1, x2, y2 = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(y2)
    while len(idxs) > 0:
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)
        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])
        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)
        overlap = (w * h) / area[idxs[:last]]
        idxs = np.delete(idxs, np.concatenate(([last], np.where(overlap > overlapThresh)[0])))
    return boxes[pick].astype("int")
    
    
def load_points_from_file(file_path):
    points = []
    shape = []
    with open(file_path, 'r') as file:
        for i, line in enumerate(file, 1):
            if i <= 4:
                x, y = map(int, line.strip().split(','))
                points.append((x, y))
            elif i == 5:
                shape= list(map(int, line.strip().split(',')))
    return points, shape



def load_real_size_from_file(file_path):
    real_size = []
    with open(file_path, 'r') as file:
        first_line = file.readline()  
        real_size = list(map(int, first_line.strip().split(',')))
    return real_size
    

def SortPoint(points):
    sp = sorted(points, key=lambda x: (int(x[1]), int(x[0])))
    if sp[0][0] > sp[1][0]:
        sp[0], sp[1] = sp[1], sp[0]
    if sp[2][0] > sp[3][0]:
        sp[2], sp[3] = sp[3], sp[2]
    return sp

def imgcorr(src, points):
    sp = SortPoint(points)
    width = int(np.sqrt(((sp[0][0] - sp[1][0]) ** 2) + (sp[0][1] - sp[1][1]) ** 2))
    height = int(np.sqrt(((sp[0][0] - sp[2][0]) ** 2) + (sp[0][1] - sp[2][1]) ** 2))
    dstrect = np.array([
        [0, 0],
        [width - 1, 0],
        [0, height - 1],
        [width - 1, height - 1]], dtype="float32")
    transform = cv2.getPerspectiveTransform(np.array(sp, dtype="float32"), dstrect)
    return cv2.warpPerspective(src, transform, (width, height))
