import time
import cv2
from picamera2 import Picamera2
from view_calibration_helper import CameraCalibrator

# 初始化相机
camera = Picamera2()

# 配置相机
camera_config = camera.create_still_configuration()
camera.configure(camera_config)

# 启动相机
camera.start()
time.sleep(5)  # 给相机一点时间预热

# 创建CameraCalibrator实例
calibrator = CameraCalibrator()

try:
    calibrator.adjust_parameters(camera)
except KeyboardInterrupt:
    camera.stop()
    print('Camera stopped.')
