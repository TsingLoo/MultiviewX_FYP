import os
import warnings

import cv2
import re
import json
import matplotlib.pyplot as plt
import numpy as np
import datasetParameters

intrinsic_camera_matrix_filenames = []
extrinsic_camera_matrix_filenames = []

def get_error(worldcoord2imgcoord_mat,validate_Points, validate_Points_3d,cam, modified = True):
    idx = 0
    error = 0
    for validate_Point_3d in validate_Points_3d:
        if(modified):
            wcoord = np.array([validate_Point_3d[0], validate_Point_3d[1], validate_Point_3d[2], 1])
        else:
            wcoord = np.array([validate_Point_3d[0], validate_Point_3d[1], 1])
            #wcoord = np.array([validate_Point_3d[0], validate_Point_3d[1], 0])

        trueimagecoord = np.array([validate_Points[idx][0], validate_Points[idx][1]])
        imgcoord = worldcoord2imgcoord_mat @ wcoord
        if(idx % 10 == 0):
            print(f"Camera{cam + 1} trueimagecoord: {trueimagecoord[0]},{trueimagecoord[1]}")
            print(f"Camera{cam + 1} imgcoordx:      {imgcoord[0] / imgcoord[2]},{imgcoord[1] / imgcoord[2]}")
            print(f"Camera{cam + 1} raw imgcoord:   {imgcoord[0]},{imgcoord[1]},{imgcoord[2]}")
            print()

        error = error + trueimagecoord[0] - imgcoord[0]/ imgcoord[2] + trueimagecoord[1] - imgcoord[1] / imgcoord[2]
        idx = idx + 1


    if( abs(error/idx) > 0.1):
        print("""   
     ___   .___________.___________. _______ .__   __. .___________. __    ______   .__   __. 
    /   \  |           |           ||   ____||  \ |  | |           ||  |  /  __  \  |  \ |  | 
   /  ^  \ `---|  |----`---|  |----`|  |__   |   \|  | `---|  |----`|  | |  |  |  | |   \|  | 
  /  /_\  \    |  |        |  |     |   __|  |  . `  |     |  |     |  | |  |  |  | |  . `  | 
 /  _____  \   |  |        |  |     |  |____ |  |\   |     |  |     |  | |  `--'  | |  |\   | 
/__/     \__\  |__|        |__|     |_______||__| \__|     |__|     |__|  \______/  |__| \__| 
                                               """)
        print(
            f"Please try to adjust the 'tRandomOffset' field and wait for the end of updates of chessborad in Unity")
        print(f"The intrinsic of this Camera{cam + 1} does NOT pass validation")
        warnings.warn(f"Failed to validate Calibration",DeprecationWarning)
        exit()

    return error/idx


def get_imgcoord2worldgrid_matrices(intrinsic_matrices, extrinsic_matrices, worldgrid2worldcoord_mat,modified = True):
    projection_matrices = {}
    errors = []
    # This block can only be used when you have got frames
    # for cam in range(datasetParameters.NUM_CAM):
    #
    #     points_2d = np.loadtxt(os.path.join('matchings',f'Camera{cam + 1}.txt'))
    #     points_3d = np.loadtxt(os.path.join('matchings',f'Camera{cam + 1}_3d.txt'))
    #     points_2d = points_2d[points_2d[:, 0] == 0, :]
    #     points_3d = points_3d[points_3d[:, 0] == 0, :]
    #     visualize_foot_image = points_2d[points_2d[:, 0] == 0, -2:]
    #     image = cv2.imread(os.path.join(datasetParameters.DATASET_NAME, f'Image_subsets/C{cam + 1}/0000.png'))
    #
    #     for point in visualize_foot_image:
    #         cv2.circle(image, tuple(point.astype(int)), 10, (0, 0, 255), -1)
    #     plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    #     plt.show()
    for cam in range(datasetParameters.NUM_CAM):
        print(f"Try to validate Camera {cam+1}")
        # print("intrinsic: ",intrinsic_matrices[cam])
        # print("extrinsic: ",extrinsic_matrices[cam])
        # print("extrinsic: ", extrinsic_matrices[cam][:,3])
        # print("extrinsic_dele: ", np.delete(extrinsic_matrices[cam], 2, 1))
        # print("extrinsic: \n", extrinsic_matrices[cam])
        # print("extrinsic: \n", extrinsic_matrices[cam])
        # print("extrinsic_dele \n: ", np.delete(extrinsic_matrices[cam], 2, 1))\

        '''np.delete(extrinsic_matrices[cam], 2, 1) deletes the third column (index 2) of the extrinsic matrix, 
            which corresponds to the translation component. 
            This is because we are only interested in the rotation component of the extrinsic matrix, 
            which determines the orientation of the camera in world coordinates.
        '''
        # print(extrinsic_matrices[cam])
        file_validatePoints = f'calib/C{cam + 1}/validatePoints.txt'
        validate_Points = np.array(np.loadtxt(file_validatePoints).astype('float32'))

        file_validatePoints_3d = f'calib/C{cam + 1}/validatePoints_3d.txt'
        validate_Points_3d = np.array(np.loadtxt(file_validatePoints_3d).astype('float32'))

        if(modified):
            # 3 X 4 = 3 x 3 X 3 x 4
            worldcoord2imgcoord_mat = intrinsic_matrices[cam] @ extrinsic_matrices[cam]

        else:
            extrinsic_matrices[cam][:, 3] = extrinsic_matrices[cam][:, 3] + extrinsic_matrices[cam][:, 2] * 0
            # print(np.delete(extrinsic_matrices[cam], 2, 1))
            worldcoord2imgcoord_mat = intrinsic_matrices[cam] @ np.delete(extrinsic_matrices[cam], 2, 1)
            # Tevc
            Tevc = extrinsic_matrices[cam][:, 3]

        errors.append(get_error(worldcoord2imgcoord_mat,validate_Points,validate_Points_3d, cam, modified))

        # image = cv2.imread(f'Image_subsets/C{cam + 1}/0000.png')
        #
        #
        # cv2.circle(image, tuple(imgcoord[0:2].astype(int)), 20, (255, 0, 0), -1)
        # plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        #
        # plt.show()
        # print("worldcoord2imgcoord_mat: ", worldcoord2imgcoord_mat)

        if(not modified):
            worldgrid2imgcoord_mat = worldcoord2imgcoord_mat @ worldgrid2worldcoord_mat
            # print("worldgrid2imgcoord_mat: ", worldgrid2imgcoord_mat)
            imgcoord2worldgrid_mat = np.linalg.inv(worldgrid2imgcoord_mat)
            # image of shape C,H,W (C,N_row,N_col); indexed as x,y,w,h (x,y,n_col,n_row)
            # matrix of shape N_row, N_col; indexed as x,y,n_row,n_col
            # print("imgcoord2worldgrid_mat: ", imgcoord2worldgrid_mat)
            permutation_mat = np.array([[0, 1, 0], [1, 0, 0], [0, 0, 1]])
            projection_matrices[cam] = permutation_mat @ imgcoord2worldgrid_mat
            print()
            pass

    return projection_matrices, errors
# def get_imgcoord2worldgrid_matrices(intrinsic_matrices, extrinsic_matrices, worldgrid2worldcoord_mat, depth_margin):
#     projection_matrices = {}
#     for cam in range(4):
#
#             # intrinsic_matrices [4,4] @ extrinsic_matrices [4,4] @ worldgrid2worldcoord_mat [4,4]
#             # inv: worldgrid2worldcoord_mat-1 @ extrinsic_matrices-1 @ intrinsic_matrices-1
#             extrinsic_matrices[cam][:,3] = extrinsic_matrices[cam][:,3]+extrinsic_matrices[cam][:,2]*i*depth_margin
#             worldcoord2imgcoord_mat = intrinsic_matrices[cam] @ np.delete(extrinsic_matrices[cam], 2, 1)
#             worldgrid2imgcoord_mat = worldcoord2imgcoord_mat @ worldgrid2worldcoord_mat
#             imgcoord2worldgrid_mat = np.linalg.inv(worldgrid2imgcoord_mat)
#             # image of shape C,H,W (C,N_row,N_col); indexed as x,y,w,h (x,y,n_col,n_row)
#             # matrix of shape N_row, N_col; indexed as x,y,n_row,n_col
#             permutation_mat = np.array([[0, 1, 0], [1, 0, 0], [0, 0, 1]]) # x->y, y->x
#             projection_matrices[(cam,i)] = permutation_mat @ imgcoord2worldgrid_mat
#     return projection_matrices

def get_intrinsic_extrinsic_matrix(camIdx):
    DATASET_NAME = os.path.join(datasetParameters.DATASET_NAME, "calibrations")
    intrinsic_path = os.path.join(DATASET_NAME,f'intrinsic')
    extrinsic_path = os.path.join(DATASET_NAME, f'extrinsic')
    fp_calibration = cv2.FileStorage(os.path.join(intrinsic_path,
                                                  intrinsic_camera_matrix_filenames[camIdx]),
                                     flags=cv2.FILE_STORAGE_READ)
    intrinsic_matrix = fp_calibration.getNode('camera_matrix').mat()
    fp_calibration.release()

    fp_calibration = cv2.FileStorage(os.path.join(extrinsic_path,
                                                  extrinsic_camera_matrix_filenames[camIdx]),
                                     flags=cv2.FILE_STORAGE_READ)
    rvec, tvec = fp_calibration.getNode('rvec').mat().squeeze(), fp_calibration.getNode('tvec').mat().squeeze()
    fp_calibration.release()

    rotation_matrix, _ = cv2.Rodrigues(rvec)
    translation_matrix = np.array(tvec, dtype=np.float32).reshape(3, 1)
    extrinsic_matrix = np.hstack((rotation_matrix, translation_matrix))
    # print()
    # print(f'Camera{camIdx + 1}\'s intrinsic_matrix is ')
    # print(f'{intrinsic_matrix} ')
    # print(f'and extrinsic_matrix is ')
    # print(f'{extrinsic_matrix}')
    return intrinsic_matrix, extrinsic_matrix

def vali(modified = True):

    for i in range(datasetParameters.NUM_CAM):
        intrinsic_xml = f'intr_Camera{i + 1}.xml'
        extrinsic_xml = f'extr_Camera{i + 1}.xml'
        intrinsic_camera_matrix_filenames.append(intrinsic_xml)
        extrinsic_camera_matrix_filenames.append(extrinsic_xml)

    # 2x4
    #worldgrid2worldcoord_mat = np.array([[0, 1/datasetParameters.MAP_EXPAND, 0, 1], [1/datasetParameters.MAP_EXPAND, 0, 0, 1]])

    # 1x4
    #worldgrid2worldcoord_mat = np.array([[1/datasetParameters.MAP_EXPAND,1/datasetParameters.MAP_EXPAND,0,1]])

    # 4x2, 此时认为gird为 2x1 的坐标。 WIDTH = 25, HEIGHT = 16 EXPAND = 40 的情况下,例如有格点坐标
    # (2,
    # 1)
    # ,经过此矩阵转换得到了，之所以如此做（4x1举证），是因为需要配合后续乘以worldcoord2imgcoord_mat（一个由3x3 乘以 3x4 矩阵相乘得到的 3x4 矩阵）（3 x 4 乘以 4 x 1 得到3x1）
    # (0.05,
    #  0.025,
    #  0,
    #  0,
    # )
    if(modified):
        worldgrid2worldcoord_mat = np.array([[1/(datasetParameters.MAP_EXPAND*datasetParameters.MAP_WIDTH),0],[0,1/(datasetParameters.MAP_EXPAND*datasetParameters.MAP_HEIGHT)],[0,0],[0,0]])
    else:
        # 3x3,猜想此时grid为2x1 齐次坐标，
        worldgrid2worldcoord_mat = np.array([[0, 0.025, 0], [0.025, 0, 0], [0, 0, 1]])

    print(worldgrid2worldcoord_mat)
    intrinsic_matrices, extrinsic_matrices = zip(*[get_intrinsic_extrinsic_matrix(cam) for cam in range(datasetParameters.NUM_CAM)])

    # for intrinsic_matrix in intrinsic_matrices:
    #     print(intrinsic_matrix)
    #     print()
    #
    # for extrinsic_matrix in extrinsic_matrices:
    #     print(extrinsic_matrix)
    #     print()

    imgcoord2worldgrid_matrices, errors = get_imgcoord2worldgrid_matrices(intrinsic_matrices, extrinsic_matrices, worldgrid2worldcoord_mat,modified)
    print("Errors are :")
    print(errors)
    print()

if __name__ == '__main__':
    vali(False)


