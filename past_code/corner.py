import numpy as np
import cv2
import time
from picamera2 import Picamera2
import os

# 确保corner文件夹存在
corner_folder = 'corner'
if not os.path.exists(corner_folder):
    os.makedirs(corner_folder)

# 将RGB颜色转换为十六进制的函数
def rgb2hex(rgb_list):
    """Converts an RGB list to a hexadecimal color code."""
    res = "#"
    for a in rgb_list:
        a_hex = hex(a)
        if a < 16:
            res += "0"
        res += a_hex[2:]
    return res

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

# 保存角点坐标到文件的函数
def save_points_to_file(points, file_path):
    with open(file_path, 'w') as file:
        for point in points:
            file.write(f"{point[0]},{point[1]}\n")

# 从文件中读取角点坐标的函数
def load_points_from_file(file_path):
    points = []
    with open(file_path, 'r') as file:
        for line in file:
            x, y = map(int, line.strip().split(','))
            points.append((x, y))
    return points

# 定义鼠标事件，用于获取像素点坐标
def on_EVENT_LBUTTONDOWN(event, x, y, flags, param):
    """Mouse callback function to get pixel color information."""
    global points, frame, display_frame
    if event == cv2.EVENT_LBUTTONDOWN:
        xy = "%d,%d" % (x, y)
        cv2.circle(display_frame, (x, y), 1, (255, 155, 0), thickness=-1)
        cv2.putText(display_frame, xy, (x+10, y+10), cv2.FONT_HERSHEY_PLAIN,
                    3.0, (0,0,0), thickness=3)
        print("x:{},y:{}".format(x, y))
        bgr_list = frame[y, x]
        rgb_list = bgr_list[::-1]
        print("RGB为: ", rgb_list)
        print("十六进制颜色：", rgb2hex(rgb_list))
        print("--" * 20)

        # 保存点击的点坐标
        points.append((x, y))
        cv2.imshow("video", display_frame)

# 初始化 Picamera2
camera = Picamera2()
camera_config = camera.create_still_configuration()  # 创建静态图片配置
camera.configure(camera_config)

# 启动相机
camera.start()
time.sleep(5)  # 给相机一点时间预热

try:
    while True:
        capture_more = input("Capture new photo? (1 to capture, 0 to exit): ")
        if capture_more.strip() == '0':
            break
        elif capture_more.strip() == '1':
            filename = f'{corner_folder}/p1.jpg'
            camera.capture_file(filename)  # 捕捉静态图片
            print(f'Captured {filename}')
            
            # 加载图片并进行处理
            frame = cv2.imread(filename)
            display_frame = frame.copy()  # 创建显示图片的副本
            if frame is not None:
                points = []  # 用于存储鼠标点击的4个点
                cv2.namedWindow('video', cv2.WINDOW_NORMAL)
                cv2.setMouseCallback("video", on_EVENT_LBUTTONDOWN)

                while(True):
                    cv2.imshow("video", display_frame)
                    if len(points) == 4:  # 当获取到4个点时，开始进行透视变换
                        dst = imgcorr(frame, points)
                        cv2.imshow("Corrected Image", dst)
                        cv2.imwrite(f'{corner_folder}/output.jpg', dst)

                        # 保存角点坐标到文件
                        save_points_to_file(points, f'{corner_folder}/points.txt')

                        # 从文件中读取角点坐标并打印
                        loaded_points = load_points_from_file(f'{corner_folder}/points.txt')
                        for i, point in enumerate(loaded_points):
                            print(f"Point {i+1}: ({point[0]}, {point[1]})")

                        break
                    c = cv2.waitKey(1)
                    if c == 27:  # ESC key to exit
                        break

                cv2.destroyAllWindows()
        else:
            print("Invalid input. Please enter 1 to capture or 0 to exit.")
except KeyboardInterrupt:
    camera.stop()
    print('Camera stopped.')
