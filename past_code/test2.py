import time
import cv2
import numpy as np
from picamera2 import Picamera2, Preview
from libcamera import controls
import io

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

def capture_image():
    """捕获图像并将其存储为内存中的 NumPy 数组"""
    stream = io.BytesIO()  # 创建内存中的字节流
    camera.capture_file(stream, format='jpeg')  # 捕获图像并将其存储到字节流中
    stream.seek(0)  # 将流的指针回到开始位置
    image = np.frombuffer(stream.read(), dtype=np.uint8)  # 从流中读取字节
    img = cv2.imdecode(image, cv2.IMREAD_COLOR)  # 将字节解码为图像
    return img

def process_image(image, template, template_gray):
    """处理图像的函数"""
    # 转换目标图像为灰度图
    target_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 获取模板的宽高
    w, h = template_gray.shape[::-1]

    # 使用模板匹配
    res = cv2.matchTemplate(target_gray, template_gray, cv2.TM_CCOEFF_NORMED)

    # 设置匹配阈值
    threshold = 0.7
    loc = np.where(res >= threshold)

    # 绘制匹配结果并计算中心点
    found = False
    for pt in zip(*loc[::-1]):
        cv2.rectangle(image, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        center_x = pt[0] + w // 2
        center_y = pt[1] + h // 2
        cv2.circle(image, (center_x, center_y), 5, (255, 0, 0), -1)
        print(f"Logo: (center_x, center_y) = ({center_x}, {center_y})")
        found = True
    if not found:
        print("Not Found")

    # 调整图像大小以适应屏幕
    screen_width = 1920
    screen_height = 1080
    resized_img = cv2.resize(image, (screen_width, screen_height))

    # 显示结果
    cv2.imshow('Detected Logo', resized_img)
    cv2.waitKey(1)  # 显示一帧，不会阻塞

# 预加载模板图像 (只加载一次)
template = cv2.imread('Genshin.jpg')
template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

try:
    while True:
        image = capture_image()  # 捕捉内存中的图像
        print('Captured image to memory')
        process_image(image, template, template_gray)  # 处理图像
        #time.sleep(5)  # 每隔5秒拍一张照片

except KeyboardInterrupt:
    camera.stop()
    print('Camera stopped.')
    cv2.destroyAllWindows()
