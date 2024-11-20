import time
import cv2
import numpy as np
from picamera2 import Picamera2, Preview
from libcamera import controls
import os

# 初始化相机
camera = Picamera2()

# 配置相机
camera_config = camera.create_still_configuration()
camera.configure(camera_config)

# 启动相机
camera.start()
time.sleep(2)  # 给相机一点时间预热

# 设置初始镜头位置
current_lens_position = 4.75
camera.set_controls({
    "AfMode": controls.AfModeEnum.Manual, 
    "LensPosition": current_lens_position,
    "ExposureTime": 5000,  # 设置曝光时间 (以微秒为单位)
    "AnalogueGain": 1.0       # 设置增益（ISO）
})

image_counter = 1

def process_image(filename):
    """处理图像的函数"""
    # 读取目标图像和模板图像
    target_img = cv2.imread(filename)
    template = cv2.imread('Genshin.jpg')

    # 转换为灰度图
    target_gray = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # 获取模板的宽高
    w, h = template_gray.shape[::-1]

    # 使用模板匹配
    res = cv2.matchTemplate(target_gray, template_gray, cv2.TM_CCOEFF_NORMED)

    # 设置匹配阈值
    threshold = 0.7
    loc = np.where(res >= threshold)

    # 绘制匹配结果并计算中心点
    for pt in zip(*loc[::-1]):
        cv2.rectangle(target_img, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        center_x = pt[0] + w // 2
        center_y = pt[1] + h // 2
        cv2.circle(target_img, (center_x, center_y), 5, (255, 0, 0), -1)
    try:
    	print(f"Logo: (center_x, center_y) = ({center_x}, {center_y})")
    except:
        print("Not Found")
    # 调整图像大小以适应屏幕
    screen_width = 1920
    screen_height = 1080
    resized_img = cv2.resize(target_img, (screen_width, screen_height))

    # 显示结果
    #cv2.imshow('Detected Logo', resized_img)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

try:
    while True:
        filename = f'p{image_counter}.jpg'
        camera.capture_file(filename)  # 捕捉静态图片
        print(f'Captured {filename}')
        process_image(filename)  # 处理图像
        image_counter += 1
        #time.sleep(10)  # 每隔5秒拍一张照片

except KeyboardInterrupt:
    camera.stop()
    print('Camera stopped.')
    cv2.destroyAllWindows()
