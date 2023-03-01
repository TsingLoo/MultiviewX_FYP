import matplotlib.pyplot as plt
import cv2
import os
from datasetParameters import *
import numpy as np
def showPoints(points2D,camIndex):

    try:
        #读取0000.png图片，应该是对于此相机的第一帧图片
        image = cv2.imread(f'Image_subsets/C{camIndex + 1}/0000.png')
        # cv2.imshow('IMREAD_COLOR+Color',image)
    except:
        try: image = cv2.imread(f'Image_subsets/C{camIndex + 1}/0000.jpg')

        except:
            print("Failed to read")

    for point in points2D:
        #print(point.astype(int))
        #cv2.circle(image, (1506, 740), 5, (0, 255, 0), -1)
        cv2.circle(image, tuple(point.astype(int)), 5, (0, 255, 0), -1)
        cv2.putText(image, str(point.astype(int)), tuple(point.astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.title(camIndex)
    plt.show()


def calibrate():
    os.makedirs('calibrations/intrinsic', exist_ok=True)
    os.makedirs('calibrations/extrinsic', exist_ok=True)
    size = (IMAGE_WIDTH, IMAGE_HEIGHT)
    #size = (IMAGE_HEIGHT, IMAGE_WIDTH)


    for cam in range(NUM_CAM):
        obj_points_3D = []  # 3d point in real world space
        img_points_2D = []  # 2d points in image plane.

        for i in range(50):
            file = f'calib/C{cam + 1}/{i}.txt'
            file3d = f'calib/C{cam + 1}/{i}_3d.txt'
            if os.path.getsize(file) == 0 or os.path.getsize(file3d) == 0:  # 文件大小为0
                os.remove(file)  # 删除这个文件
                os.remove(file3d)  # 删除这个文件
            else:
                corners2 = np.loadtxt(file)
                if(len(corners2)>5):
                    corners2 = np.array(corners2.astype('float32'))
                    obj_3D = np.array(np.loadtxt(file3d).astype('float32'))
                    # print(type(obj_3D))
                    # print(obj_3D)
                    obj_points_3D.append(obj_3D)
                    img_points_2D.append(corners2)


        #showPoints(points_2d,cam)
        #points_2d = np.concatenate(points_2d, axis=0).reshape([1, -1, 2]).astype('float32')
        #points_3d = np.concatenate(points_3d, axis=0).reshape([1, -1, 3]).astype('float32')
        print(type(obj_points_3D))

        #print(obj_points_3D)
        #通过给定的信息求出此摄像机的信息矩阵
        #cameraMatrix = cv2.initCameraMatrix2D(points_3d, points_2d, size)
        cameraMatrix = cv2.initCameraMatrix2D(obj_points_3D,  img_points_2D, size, 1)

        #重投影误差,越小越好，内参矩阵，dist相机畸变函数， rvecs 标定棋盘格世界坐标系到相机坐标系的旋转函数 平移参数
        #https://docs.opencv.org/3.4/dc/dbb/tutorial_py_calibration.html
        #0.0004178419607408868 [[899.99963677   0.         959.99969735] [  0.         899.99954514 540.00000687][  0.           0.           1.        ]]
        #[[ 9.46976752e-07 -1.57584887e-06  1.76995464e-08 -1.60416686e-07 5.67520302e-07]] (array([[-4.81027129e-07],[-1.91248031e+00],[-2.49239284e+00]]),)
        retval, cameraMatrix, distCoeffs, rvecs, tvecs = \
            cv2.calibrateCamera(obj_points_3D,  img_points_2D, size, cameraMatrix, None,flags = cv2.CALIB_USE_INTRINSIC_GUESS)


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


        print(f"==== Calibrate {cam + 1} HAS DONE ====");
    pass


if __name__ == '__main__':
    calibrate()

