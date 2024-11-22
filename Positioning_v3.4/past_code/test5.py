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

# 读取相机参数和畸变系数
def load_calibration_params():
    """从文件加载相机内参和畸变系数"""
    with open('calibration_results.txt', 'r') as f:
        lines = f.readlines()

    # 提取内参矩阵
    intrinsic_matrix = np.array([[float(val) for val in lines[1].split()],
                                 [float(val) for val in lines[2].split()],
                                 [float(val) for val in lines[3].split()]])

    # 提取畸变系数
    distortion_coeffs = np.array([float(val) for val in lines[6:11]])

    return intrinsic_matrix, distortion_coeffs

def undistort_image(image, intrinsic_matrix, distortion_coeffs):
    """校正图像中的畸变"""
    h, w = image.shape[:2]
    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(intrinsic_matrix, distortion_coeffs, (w, h), 1, (w, h))
    undistorted_image = cv2.undistort(image, intrinsic_matrix, distortion_coeffs, None, new_camera_matrix)

    # 裁剪图像以去除黑边，确保裁剪后的图像有效
    x, y, w, h = roi
    if w > 0 and h > 0:
        undistorted_image = undistorted_image[y:y+h, x:x+w]

    return undistorted_image

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

# 从文件中读取角点坐标的函数
def load_points_from_file(file_path):
    points = []
    with open(file_path, 'r') as file:
        for line in file:
            x, y = map(int, line.strip().split(','))
            points.append((x, y))
    return points

# 对角点进行排序的函数
def SortPoint(points):
    sp = sorted(points, key=lambda x: (int(x[1]), int(x[0])))
    if sp[0][0] > sp[1][0]:
        sp[0], sp[1] = sp[1], sp[0]
    
    if sp[2][0] > sp[3][0]:
        sp[2], sp[3] = sp[3], sp[2]
    
    return sp

# 透视变换的函数
def imgcorr(src, points):
    # 确保points输入的是4个角点
    if len(points) != 4:
        raise ValueError("需要输入四个角点")

    # 手动输入的角点要进行排序
    sp = SortPoint(points)

    # 计算四边形的宽度和高度
    width = int(np.sqrt(((sp[0][0] - sp[1][0]) ** 2) + (sp[0][1] - sp[1][1]) ** 2))
    height = int(np.sqrt(((sp[0][0] - sp[2][0]) ** 2) + (sp[0][1] - sp[2][1]) ** 2))

    # 定义目标矩形的四个角点
    dstrect = np.array([
        [0, 0],
        [width - 1, 0],
        [0, height - 1],
        [width - 1, height - 1]], dtype="float32")

    # 透视变换矩阵
    transform = cv2.getPerspectiveTransform(np.array(sp, dtype="float32"), dstrect)
    
    # 应用透视变换
    warpedimg = cv2.warpPerspective(src, transform, (width, height))

    return warpedimg


def process_image(image, template, template_gray, intrinsic_matrix, distortion_coeffs, points):
    """处理图像的函数"""
    try:
        # 畸变校正
        #undistorted_image = undistort_image(image, intrinsic_matrix, distortion_coeffs)
        
        # 透视变换
        warped_image = imgcorr(image, points)

        # 转换目标图像为灰度图
        target_gray = cv2.cvtColor(warped_image, cv2.COLOR_BGR2GRAY)

        # 获取模板的宽高
        w, h = template_gray.shape[::-1]

        # 使用模板匹配
        res = cv2.matchTemplate(target_gray, template_gray, cv2.TM_CCOEFF_NORMED)

        # 设置匹配阈值
        threshold = 0.8
        loc = np.where(res >= threshold)

        # 储存匹配区域
        boxes = []
        for pt in zip(*loc[::-1]):
            boxes.append([pt[0], pt[1], pt[0] + w, pt[1] + h])

        # 应用非最大抑制以去除冗余的框
        boxes = non_max_suppression(boxes)

        # 绘制匹配结果并计算中心点
        display_image = warped_image.copy()  # Make a fresh copy of the image for display purposes
        if len(boxes) == 0:
            print("Not Found")
        else:
            for (x1, y1, x2, y2) in boxes:
                cv2.rectangle(display_image, (x1, y1), (x2, y2), (0, 0, 255), 2)
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                cv2.circle(display_image, (center_x, center_y), 5, (255, 0, 0), -1)
                print(f"Logo: (center_x, center_y) = ({center_x}, {center_y})")

        # 调整图像大小以适应屏幕
        screen_width = 1920
        screen_height = 1080
        resized_img = cv2.resize(display_image, (screen_width, screen_height))

        # 显示结果
        cv2.imshow('Detected Logo', resized_img)
        cv2.waitKey(30)  # 延长显示时间，确保图像可以看清
    except Exception as e:
        print(f"Error during image processing: {e}")


# 主程序循环
if __name__ == "__main__":
    # 加载相机参数
    intrinsic_matrix, distortion_coeffs = load_calibration_params()

    # 加载模板图像和灰度图像
    template = cv2.imread('template.jpg')  # 读取模板图像
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)  # 转换为灰度图

    # 从文件加载角点
    points = load_points_from_file('corner/points.txt')

    try:
        while True:
            # 捕捉图像
            image = capture_image()
            print('Captured image to memory')

            # 处理图像
            process_image(image, template, template_gray, intrinsic_matrix, distortion_coeffs, points)

    except KeyboardInterrupt:
        print("程序中断，退出...")
    finally:
        # 释放资源
        camera.stop()
        cv2.destroyAllWindows()
