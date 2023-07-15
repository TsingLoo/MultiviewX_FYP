import matplotlib.pyplot as plt
import cv2
import os
from concurrent.futures import ThreadPoolExecutor
import datasetParameters
from unitConversion import *
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

def calibrate_camera(cam):
    DATASET_NAME = os.path.join(datasetParameters.DATASET_NAME, "calibrations")
    intrinsic_path = os.path.join(DATASET_NAME,f'intrinsic')
    extrinsic_path = os.path.join(DATASET_NAME, f'extrinsic')
    os.makedirs(intrinsic_path, exist_ok=True)
    os.makedirs(extrinsic_path, exist_ok=True)
    size = (IMAGE_WIDTH, IMAGE_HEIGHT)    

    print(f"==== Processing Camera {cam + 1} =====")
    obj_points_3D = []  # 3d point in real world space
    img_points_2D = []  # 2d points in image plane.

    file_markPoints = f'calib/C{cam + 1}/markPoints.txt'
    file_markPoints_3d = f'calib/C{cam + 1}/markPoints_3d.txt'

    file_validatePoints = f'calib/C{cam + 1}/validatePoints.txt'
    file_validatePoints_3d = f'calib/C{cam + 1}/validatePoints_3d.txt'

    mark_points_2D = np.array(np.loadtxt(file_markPoints).astype('float32'))
    mark_points_3D = np.array(np.loadtxt(file_markPoints_3d).astype('float32'))

    validate_Points_2D = np.array(np.loadtxt(file_validatePoints).astype('float32'))
    validate_Points_3D = np.array(np.loadtxt(file_validatePoints_3d).astype('float32'))

    #for i in range(0, len(mark_points_3D)):
        #mark_points_3D[i] = get_opencv_coordinates(mark_points_3D[i])
    #    mark_points_3D[i] = process_worldcoord(mark_points_3D[i])
    #    print(mark_points_3D[i])
    #
    #for i in range(0, len(validate_Points_3D)):
        #validate_Points_3D[i] = get_opencv_coordinates(validate_Points_3D[i])
    #    validate_Points_3D[i] = process_worldcoord(validate_Points_3D[i])

    #print(mark_points_3D)

    #print(mark_points_3D)


    for i in range(datasetParameters.CHESSBOARD_COUNT):
        file = f'calib/C{cam + 1}/{i}.txt'
        file3d = f'calib/C{cam + 1}/{i}_3d.txt'
        if os.path.exists(file) and os.path.exists(file3d):
            if os.path.getsize(file) == 0 or os.path.getsize(file3d) == 0:  # 文件大小为0
                os.remove(file)  # 删除这个文件
                os.remove(file3d)  # 删除这个文件
            else:
                corners2 = np.loadtxt(file)
                if(len(corners2)>10):
                    corners2 = np.array(corners2.astype('float32'))
                    obj_3D = np.array(np.loadtxt(file3d).astype('float32'))
                    # print(type(obj_3D))
                    # print(obj_3D)
                    obj_points_3D.append(obj_3D)
                    img_points_2D.append(corners2)

    print(f"Camera {cam + 1} IO Pass")
    #showPoints(points_2d,cam)
    #points_2d = np.concatenate(points_2d, axis=0).reshape([1, -1, 2]).astype('float32')
    #points_3d = np.concatenate(points_3d, axis=0).reshape([1, -1, 3]).astype('float32')
    #print(type(obj_points_3D))

    #print(obj_points_3D)
    #通过给定的信息求出此摄像机的信息矩阵
    #cameraMatrix = cv2.initCameraMatrix2D(points_3d, points_2d, size)
    cameraMatrix = cv2.initCameraMatrix2D(obj_points_3D,  img_points_2D, size, 1)
    print(f"Init CameraMatrix {cam + 1} Pass")

    #重投影误差,越小越好，内参矩阵，dist相机畸变函数， rvecs 标定棋盘格世界坐标系到相机坐标系的旋转函数 平移参数
    #https://docs.opencv.org/3.4/dc/dbb/tutorial_py_calibration.html
    #0.0004178419607408868 [[899.99963677   0.         959.99969735] [  0.         899.99954514 540.00000687][  0.           0.           1.        ]]
    #[[ 9.46976752e-07 -1.57584887e-06  1.76995464e-08 -1.60416686e-07 5.67520302e-07]] (array([[-4.81027129e-07],[-1.91248031e+00],[-2.49239284e+00]]),)
    retval, cameraMatrix, distCoeffs, rvecs, tvecs = \
        cv2.calibrateCamera(obj_points_3D,  img_points_2D, size, cameraMatrix, None,flags = cv2.CALIB_USE_INTRINSIC_GUESS,)



    print(f"Calibrate Camera {cam + 1} Pass")

    #print(mark_points_3D)
    #print(mark_points_2D)
    _,R,T = cv2.solvePnP(mark_points_3D,mark_points_2D,cameraMatrix,distCoeffs)

    RMat = cv2.Rodrigues(R)[0]

    print(f"Rotation Matrix of {cam + 1} is ")
    print(RMat)

    #
    mean_error = 0
    imgpoints2, _ = cv2.projectPoints(validate_Points_3D, R, T, cameraMatrix, distCoeffs)
    imgpoints2 = np.squeeze(imgpoints2)
    error = cv2.norm(validate_Points_2D, imgpoints2, cv2.NORM_L2)/len(imgpoints2)
    mean_error += error


    print("total error by validate: {}".format(mean_error/len(validate_Points_3D)) )
    print("total error by calibrate: {}".format(retval))
    if((mean_error/len(validate_Points_3D) - retval)) > 0.001:
        print(f"The input data ({len(obj_points_3D)} tuples) for this Camera{cam + 1} is too little")
        print(f"The intrinsic of this Camera{cam + 1} will be unstable and unreliable" )
        print(f"Please try to adjust the 'tRandomOffset' field and wait for the end of updates of chessborad in Unity")

    f = cv2.FileStorage(os.path.join(intrinsic_path,f'intr_Camera{cam + 1}.xml') , flags=cv2.FILE_STORAGE_WRITE)
    f.write(name='camera_matrix', val=cameraMatrix)
    f.write(name='distortion_coefficients', val=distCoeffs)
    f.release()



    f = cv2.FileStorage(os.path.join(extrinsic_path, f'extr_Camera{cam + 1}.xml'), flags=cv2.FileStorage_WRITE)
    f.write(name='rvec', val=R)
    f.write(name='tvec', val=T)

    f.release()

    #print(retval)
    print(f"==== Calibrate {cam + 1} has done ====");
    print()




def calibrate():
    with ThreadPoolExecutor() as executor:
        executor.map(calibrate_camera, range(NUM_CAM))



if __name__ == '__main__':
    calibrate()

