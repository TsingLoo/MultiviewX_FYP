import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
from datasetParameters import *

size = (IMAGE_HEIGHT, IMAGE_WIDTH)
#size = (IMAGE_WIDTH, IMAGE_HEIGHT)


def calibrate():
    os.makedirs('calibrations/intrinsic', exist_ok=True)
    os.makedirs('calibrations/extrinsic', exist_ok=True)
    for cam in range(NUM_CAM):
        points_2d = np.loadtxt(f'matchings/Camera{cam + 1}.txt')
        points_3d = np.loadtxt(f'matchings/Camera{cam + 1}_3D.txt')

        #x[:,n]表示在全部数组（维）中取第n个数据，直观来说，x[:,n]就是取所有集合的第n个数据,即第一列数据
        #[:,0]表示[  0.   0.   0. ... 399. 399. 399.]

        #数据以行呈现
        points_2d = points_2d[points_2d[:, 0] == 0, :]
        #print(points_2d)

        points_3d = points_3d[points_3d[:, 0] == 0, :]

        # 最后一个坐标是脚底的位置
        #坐标数组 ... [1723.596   471.1655] [1421.27    544.6304]
        visualize_foot_image = points_2d[points_2d[:, 0] == 0, -2:]

        #print(visualize_foot_image)

        try:
            #读取0000.png图片，应该是对于此相机的第一帧图片
            image = cv2.imread(f'Image_subsets/C{cam + 1}/0000.png')
            # cv2.imshow('IMREAD_COLOR+Color',image)
        except:
            try: image = cv2.imread(f'Image_subsets/C{cam + 1}/0000.jpg')

            except:
                print("Failed to read")

        #将二维的脚底点标注在这张图片上
        for point in visualize_foot_image:
            #print(point.astype(int))
            #cv2.circle(image, (1506, 740), 5, (0, 255, 0), -1)
            cv2.circle(image, tuple(point.astype(int)), 5, (0, 255, 0), -1)
            cv2.putText(image, str(point.astype(int)), tuple(point.astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.title(cam + 1)
        plt.show()


        points_2d_list, points_3d_list = [], []


        for view in range(9):
            points_2d_list.append(points_2d[:, 2 * view + 2:2 * (view + 1) + 2])
            points_3d_list.append(points_3d[:, 3 * view + 2:3 * (view + 1) + 2])
            #print(points_2d_list)

#        [[1   2   3]
#        [111 222 333]]

#       矩阵a的维度为: (2, 3)
#        [[4  5  6]
#         [44 55 67]]

#        axis = 0
#        的结果为:
#        [[1   2   3]
#         [111 222 333]
#         [4   5   6]
#         [44  55  67]]

        points_2d = np.concatenate(points_2d_list, axis=0).reshape([1, -1, 2]).astype('float32')
        print(points_2d)

        #世界坐标中的高度等等信息
        points_3d = np.concatenate(points_3d_list, axis=0).reshape([1, -1, 3]).astype('float32')

        #print(points_3d)

        #print(type(points_3d))
        #通过给定的信息求出此摄像机的信息矩阵
        #cameraMatrix = cv2.initCameraMatrix2D(points_3d, points_2d, (IMAGE_WIDTH,IMAGE_HEIGHT))
        cameraMatrix = cv2.initCameraMatrix2D(points_3d, points_2d, size,1 )

        #重投影误差,越小越好，内参矩阵，dist相机畸变函数， rvecs 标定棋盘格世界坐标系到相机坐标系的旋转函数 平移参数
        #https://docs.opencv.org/3.4/dc/dbb/tutorial_py_calibration.html
        #0.0004178419607408868 [[899.99963677   0.         959.99969735] [  0.         899.99954514 540.00000687][  0.           0.           1.        ]]
        #[[ 9.46976752e-07 -1.57584887e-06  1.76995464e-08 -1.60416686e-07 5.67520302e-07]] (array([[-4.81027129e-07],[-1.91248031e+00],[-2.49239284e+00]]),)
        retval, cameraMatrix, distCoeffs, rvecs, tvecs = \
            cv2.calibrateCamera(points_3d, points_2d, size, cameraMatrix, None,
                                flags=cv2.CALIB_USE_INTRINSIC_GUESS + cv2.CALIB_FIX_ASPECT_RATIO)


        print(len(points_3d) + len(points_2d) )

        #给出了畸变参数
        #print(tvecs)

        f = cv2.FileStorage(f'calibrations/intrinsic/intr_Camera{cam + 1}.xml', flags=cv2.FILE_STORAGE_WRITE)
        f.write(name='camera_matrix', val=cameraMatrix)
        f.write(name='distortion_coefficients', val=distCoeffs)
        f.release()
        f = cv2.FileStorage(f'calibrations/extrinsic/extr_Camera{cam + 1}.xml', flags=cv2.FileStorage_WRITE)
        f.write(name='rvec', val=rvecs[0])
        f.write(name='tvec', val=tvecs[0])
        f.release()


        print("Calibrate HAS DONE =================================================================");
    pass


if __name__ == '__main__':
    calibrate()
