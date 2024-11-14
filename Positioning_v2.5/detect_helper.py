# detect_helper.py
import time
import cv2
import numpy as np
from picamera2 import Picamera2, Preview
from libcamera import controls
import io


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
        time.sleep(2)  # Wait for the camera to start
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


class DetectProcessor:
    def __init__(self):
        """Initialize the camera and configure settings."""
        self.points = []
        self.shape = []
        self.real_size = []

    def load_points_from_file(self, file_path):
        with open(file_path, 'r') as file:
            for i, line in enumerate(file, 1):
                if i <= 4:
                    x, y = map(int, line.strip().split(','))
                    self.points.append((x, y))
                elif i == 5:
                    self.shape = list(map(int, line.strip().split(',')))

    def load_real_size_from_file(self, file_path):
        with open(file_path, 'r') as file:
            first_line = file.readline()
            self.real_size = list(map(int, first_line.strip().split(',')))

    def SortPoint(self):
        sp = sorted(self.points, key=lambda x: (int(x[1]), int(x[0])))
        if sp[0][0] > sp[1][0]:
            sp[0], sp[1] = sp[1], sp[0]
        if sp[2][0] > sp[3][0]:
            sp[2], sp[3] = sp[3], sp[2]
        return sp

    def imgcorr(self, src):
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

    def process_image(self, path_template, path_parameters_points, path_parameters_real_size, camera):
        """Process the image and perform template matching."""
        template = cv2.imread(path_template)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        self.points.clear()
        self.shape.clear()
        self.real_size.clear()
        self.load_points_from_file(path_parameters_points)
        self.load_real_size_from_file(path_parameters_real_size)

        try:
            end = False
            while not end:
                image = camera.capture_image()
                print('Captured image to memory')
                
                try:
                    warped_image = self.imgcorr(image)
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
                    cv2.namedWindow('Detected Logo' + self.__class__.__name__, cv2.WINDOW_NORMAL)
                    cv2.imshow('Detected Logo', display_image)
                    cv2.waitKey(30)
                except Exception as e:
                    print(f"Error during image processing: {e}")

        except KeyboardInterrupt:
            print("Keyboard Interrupt")
        finally:
            cv2.destroyAllWindows()