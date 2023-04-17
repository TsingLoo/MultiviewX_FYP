import os
import cv2
from unitConversion import *


intrinsic_camera_matrix_filenames = []
extrinsic_camera_matrix_filenames = []

#拿到了计算机的畸变参数
def generate_cam_pom(rvec, tvec, cameraMatrix, distCoeffs):

    #print(tvec)
    #print(cameraMatrix)
    #print(distCoeffs)
    # WILDTRACK has irregular denotion: H*W=480*1440, normally x would be \in [0,1440), not [0,480)
    # In our data annotation, we follow the regular x \in [0,W), and one can calculate x = pos % W, y = pos // W
    #将给定的地图转化为2维坐标

    #此处的pos是从0-639999的数组[     0      1      2 ... 639997 639998 639999]
    coord_x, coord_y = get_worldcoord_from_pos(np.arange(MAP_HEIGHT * MAP_WIDTH * MAP_EXPAND * MAP_EXPAND))


    #print(MAP_WIDTH)
    #print(MAP_HEIGHT)
    #print(MAP_EXPAND)
    #print("coord_x:" + str(coord_x) + " coord_y: " + str(coord_y))

    #将制作好的格点成对压入
    centers3d = np.stack([coord_x, coord_y, np.zeros_like(coord_y)], axis=1)
    #print(centers3d)
    #print(centers3d)
    #print("======")

    #列的列
    #创造出所有可能的，人的3D的限制点，脚四个，头四个，共8x64000个
    points3d8s = []
    points3d8s.append(centers3d + np.array([MAN_RADIUS, MAN_RADIUS, 0]))
    points3d8s.append(centers3d + np.array([-MAN_RADIUS, MAN_RADIUS, 0]))
    points3d8s.append(centers3d + np.array([MAN_RADIUS, -MAN_RADIUS, 0]))
    points3d8s.append(centers3d + np.array([-MAN_RADIUS, -MAN_RADIUS, 0]))
    points3d8s.append(centers3d + np.array([MAN_RADIUS, MAN_RADIUS, MAN_HEIGHT]))
    points3d8s.append(centers3d + np.array([-MAN_RADIUS, MAN_RADIUS, MAN_HEIGHT]))
    points3d8s.append(centers3d + np.array([MAN_RADIUS, -MAN_RADIUS, MAN_HEIGHT]))
    points3d8s.append(centers3d + np.array([-MAN_RADIUS, -MAN_RADIUS, MAN_HEIGHT]))


    #print(points3d8s)
    #shape[0]输出行数
    #print([centers3d.shape[0], 4])


    #数量等同于地面格点数(640000)的,[W,D,1,1]？也许是下一步计算之前，准备好2D包围盒，目前都是整个照片大小的盒子
    bbox = np.ones([centers3d.shape[0], 4]) * np.array([IMAGE_WIDTH, IMAGE_HEIGHT, 0, 0])  # xmin,ymin,xmax,ymax


    for i in range(8):  # for all 8 points，
        #这里给出了目前划分中，人最多能得到的位置
        points_img, _ = cv2.projectPoints(points3d8s[i], rvec, tvec, cameraMatrix, distCoeffs)
        points_img = points_img.squeeze()

        #So it returns a 1D array of all the x-coordinates of the projected 3D points in image space.
        bbox[:, 0] = np.min([bbox[:, 0], points_img[:, 0]], axis=0)  # xmin 左下点x
        bbox[:, 1] = np.min([bbox[:, 1], points_img[:, 1]], axis=0)  # ymin 左下点y
        bbox[:, 2] = np.max([bbox[:, 2], points_img[:, 0]], axis=0)  # xmax
        bbox[:, 3] = np.max([bbox[:, 3], points_img[:, 1]], axis=0)  # ymax 右上y

        pass

    #某种程度上描述了这个相机中，能画框的最边界位置，不然就不画框框了
    points_img, _ = cv2.projectPoints(centers3d, rvec, tvec, cameraMatrix, distCoeffs)
    points_img = points_img.squeeze()
    #右上的y
    bbox[:, 3] = points_img[:, 1]
    # offset = points_img[:, 0] - (bbox[:, 0] + bbox[:, 2]) / 2
    # bbox[:, 0] += offset
    # bbox[:, 2] += offset

    #640000个，默认全是0也就是都看得见
    notvisible = np.zeros([centers3d.shape[0]])


                    #左下角x超出了图像宽，出现在图像外右侧 左下角y超出了图像高，出现在图像上方
    notvisible += (bbox[:, 0] >= IMAGE_WIDTH - 2) + (bbox[:, 1] >= IMAGE_HEIGHT - 2) + (bbox[:, 2] <= 1) + (bbox[:, 3] <= 1)
    # 2D矩形是合着的
    notvisible += bbox[:, 2] - bbox[:, 0] > bbox[:, 3] - bbox[:, 1]  # w > h
    # 人很瘦长
    notvisible += (bbox[:, 2] - bbox[:, 0] > IMAGE_WIDTH / 3)  # + (bbox[:, 3] - bbox[:, 1] > IMAGE_HEIGHT / 3)
    #print(len(notvisible))
    return bbox.astype(int), notvisible.astype(bool)


def generate_POM():
    for i in range(NUM_CAM):
        intrinsic_xml = f'intr_Camera{i + 1}.xml'
        extrinsic_xml = f'extr_Camera{i + 1}.xml'
        intrinsic_camera_matrix_filenames.append(intrinsic_xml)
        extrinsic_camera_matrix_filenames.append(extrinsic_xml)
    DATASET_NAME = datasetParameters.DATASET_NAME
    calibration_path = os.path.join(datasetParameters.DATASET_NAME, "calibrations")
    intrinsic_path = os.path.join(calibration_path, f'intrinsic')
    extrinsic_path = os.path.join(calibration_path, f'extrinsic')
    fpath = os.path.join(DATASET_NAME,'rectangles.pom')
    if os.path.exists(fpath):
        os.remove(fpath)
    fp = open(fpath, 'w')
    errors = []
    for cam in range(NUM_CAM):

        fp_calibration = cv2.FileStorage(os.path.join(intrinsic_path,  f'{intrinsic_camera_matrix_filenames[cam]}'),
                                         flags=cv2.FILE_STORAGE_READ)

        #取得给定的相机参数
        cameraMatrix, distCoeffs = fp_calibration.getNode('camera_matrix').mat(), fp_calibration.getNode(
            'distortion_coefficients').mat()

        fp_calibration.release()
        fp_calibration = cv2.FileStorage(os.path.join(extrinsic_path,f'{extrinsic_camera_matrix_filenames[cam]}')  ,
                                         flags=cv2.FILE_STORAGE_READ)
        rvec, tvec = fp_calibration.getNode('rvec').mat().squeeze(), fp_calibration.getNode('tvec').mat().squeeze()
        #取得给定的相机外参
        fp_calibration.release()

        #准备画框
        bbox, notvisible = generate_cam_pom(rvec, tvec, cameraMatrix, distCoeffs)  # xmin,ymin,xmax,ymax

        #print(bbox)

        #对于地面上的640000个点来说
        for pos in range(len(notvisible)):
            #如果这个点不会出现在相机中，
            if notvisible[pos]:
                fp.write(f'RECTANGLE {cam} {pos} notvisible\n')
            else:
                #如果这个点在了相机之中
                fp.write(f'RECTANGLE {cam} {pos} '
                         f'{bbox[pos, 0]} {bbox[pos, 1]} {bbox[pos, 2]} {bbox[pos, 3]}\n')

        foot_3d = get_worldcoord_from_pos(np.arange(len(notvisible)))

        #print(notvisible)
        foot_3d = np.concatenate([foot_3d, np.zeros([1, len(notvisible)])], axis=0).transpose()[
                  (1 - notvisible).astype(bool), :].reshape([1, -1, 3])

        #print(foot_3d)
        #print(foot_3d)




        projected_foot_2d, _ = cv2.projectPoints(foot_3d, rvec, tvec, cameraMatrix, distCoeffs)
        projected_foot_2d = projected_foot_2d.squeeze()
        foot_2d = np.array([(bbox[:, 0] + bbox[:, 2]) / 2, bbox[:, 3]]).transpose()[(1 - notvisible).astype(bool), :]
        #print(foot_2d)
        projected_foot_2d = np.maximum(projected_foot_2d, 0)
        projected_foot_2d = np.minimum(projected_foot_2d, [IMAGE_WIDTH, IMAGE_HEIGHT])
        foot_2d = np.maximum(foot_2d, 0)
        foot_2d = np.minimum(foot_2d, [IMAGE_WIDTH, IMAGE_HEIGHT])
        errors.append(np.linalg.norm(projected_foot_2d - foot_2d, axis=1))
        print(f"==== POM Cam {cam +1} has done ====")
    errors = np.concatenate(errors)
    print(f'average error in image pixels: {np.average(errors) / NUM_CAM}')
    fp.close()
    pass


if __name__ == '__main__':
    generate_POM()
