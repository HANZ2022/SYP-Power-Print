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

def non_max_suppression(boxes, overlapThresh=0.3):
    """实现非最大值抑制算法以过滤冗余的框"""
    if len(boxes) == 0:
        return []
    
    boxes = np.array(boxes)
    if boxes.dtype.kind == "i":
        boxes = boxes.astype("float")
    
    pick = []
    
    # 坐标提取
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]
    
    # 计算区域面积和排序
    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(y2)
    
    while len(idxs) > 0:
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)
        
        # 计算交叠区域
        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])
        
        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)
        
        overlap = (w * h) / area[idxs[:last]]
        
        idxs = np.delete(idxs, np.concatenate(([last], np.where(overlap > overlapThresh)[0])))
    
    return boxes[pick].astype("int")

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

    # 储存匹配区域
    boxes = []
    for pt in zip(*loc[::-1]):
        boxes.append([pt[0], pt[1], pt[0] + w, pt[1] + h])

    # 应用非最大抑制以去除冗余的框
    boxes = non_max_suppression(boxes)

    # 绘制匹配结果并计算中心点
    if len(boxes) == 0:
        print("Not Found")
    else:
        for (x1, y1, x2, y2) in boxes:
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            cv2.circle(image, (center_x, center_y), 5, (255, 0, 0), -1)
            print(f"Logo: (center_x, center_y) = ({center_x}, {center_y})")

    # 调整图像大小以适应屏幕
    screen_width = 1920
    screen_height = 1080
    resized_img = cv2.resize(image, (screen_width, screen_height))

    # 显示结果
    cv2.imshow('Detected Logo', resized_img)
    cv2.waitKey(0)  # 显示一帧，不会阻塞

# 预加载模板图像 (只加载一次)
template = cv2.imread('Genshin.jpg')
template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

try:
    while True:
        image = capture_image()  # 捕捉内存中的图像
        print('Captured image to memory')
        process_image(image, template, template_gray)  # 处理图像
        time.sleep(5)  # 每隔5秒拍一张照片

except KeyboardInterrupt:
    camera.stop()
    print('Camera stopped.')
    cv2.destroyAllWindows()
