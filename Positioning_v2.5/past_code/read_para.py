import numpy as np

def load_calibration_params(file_path='calibration_results.txt'):
    """从文件加载相机内参和畸变系数"""
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # 初始化内参矩阵和畸变系数列表
    intrinsic_matrix = []
    distortion_coeffs = []

    # 提取内参矩阵
    intrinsic_matrix = np.array([[float(val) for val in lines[1].split()],
                                 [float(val) for val in lines[2].split()],
                                 [float(val) for val in lines[3].split()]])

    # 提取畸变系数
    distortion_coeffs = np.array([float(val) for val in lines[6:11]])
 
   # 将内参矩阵转换为NumPy数组
    intrinsic_matrix = np.array(intrinsic_matrix)

    # 将畸变系数列表转换为NumPy数组
    distortion_coeffs = np.array(distortion_coeffs)
    return intrinsic_matrix, distortion_coeffs
# 调用函数并打印结果
intrinsic_matrix, distortion_coeffs = load_calibration_params()
print("Intrinsic Matrix:\n", intrinsic_matrix)
print("Distortion Coefficients:\n", distortion_coeffs)
