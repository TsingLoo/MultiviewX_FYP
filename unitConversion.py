import numpy as np
import os
import cv2
import datasetParameters
from datasetParameters import *

def get_worldgrid_from_pos(pos):
    """
This method takes an index of points(if pos = 2, it means input the second point) and returns the
corordinates of the point in world grdid form。
for input 3 , the return value is [0.075,0]
例如对于第0个点（输入值为0），坐标为（0，0），对于第999个点（输入值为999），坐标为(999,0),对于第1000个点（输入值为1000），坐标为(0,1)
    :param pos:
    :return:
    """
# '%' means take the remainder, 10%3 = 1
# '//' means round donw, 9//2 = 4, -9//2 = -4，可以得到纵坐标，总数除以一行可以容纳的数量，向下取整，可以得知前面已经有几行
    grid_x = pos % (MAP_WIDTH * MAP_EXPAND)
    grid_y = pos // (MAP_WIDTH * MAP_EXPAND)
    return np.array([grid_x, grid_y], dtype=int)


def get_pos_from_worldgrid(worldgrid):
    grid_x, grid_y = worldgrid
    return grid_x + grid_y * MAP_WIDTH * MAP_EXPAND


def get_worldgrid_from_worldcoord(world_coord):

    coord_x, coord_y = world_coord
    grid_x = coord_x * MAP_EXPAND
    grid_y = coord_y * MAP_EXPAND
    return np.array([grid_x, grid_y], dtype=int)


def get_worldcoord_from_worldgrid(worldgrid):
    """
拿到网格坐标后，可以转换为真正的世界坐标。具体办法也很简单，将刚刚的刻度E除回去就行
    :param worldgrid:
    :return:
    """


    grid_x, grid_y = worldgrid
    coord_x = grid_x / MAP_EXPAND
    coord_y = grid_y / MAP_EXPAND
    return np.array([coord_x, coord_y])


def get_worldcoord_from_pos(pos):
    """
This method takes an index of points(if pos = 2, it means input the second point) and returns the
corordinates of the point in world coordinates form
for input 3 , the return value is [0.075,0]
    :param pos:
    :return:
    """
    grid = get_worldgrid_from_pos(pos)
    return get_worldcoord_from_worldgrid(grid)


def get_pos_from_worldcoord(world_coord):
    grid = get_worldgrid_from_worldcoord(world_coord)
    return get_pos_from_worldgrid(grid)

def process_worldcoord(unity_pos):
    result = get_transformed_coordinates(unity_pos)
    #result = swap_unity23(unity_pos)

    return result

def get_transformed_coordinates(unity_pos):
    unity_pos = unity_pos / datasetParameters.Scaling

    if(len(unity_pos) == 3):

        result = [unity_pos[0] -  GRID_ORIGIN[0], unity_pos[2] -  GRID_ORIGIN[2], unity_pos[1] - GRID_ORIGIN[1]]

    if(len(unity_pos) == 2):
        result = [unity_pos[0] -  GRID_ORIGIN[0], unity_pos[2] -  GRID_ORIGIN[2]]
    return result
def swap_unity23(unity_pos_3):
    result = [unity_pos_3[0],unity_pos_3[2],unity_pos_3[1]]
    return result

def swap_unity12(unity_pos_2):
    result = [unity_pos_2[0],unity_pos_2[2],unity_pos_2[1]]
    return result


def get_calibration(camIdx):
    camIdx = camIdx + 1
    intrinsic_xml = f'intr_Camera{camIdx}.xml'
    extrinsic_xml = f'extr_Camera{camIdx}.xml'


    DATASET_NAME = datasetParameters.DATASET_NAME
    calibration_path = os.path.join(DATASET_NAME, "calibrations")
    intrinsic_path = os.path.join(calibration_path, f'intrinsic')
    extrinsic_path = os.path.join(calibration_path, f'extrinsic')

    fp_calibration = cv2.FileStorage(os.path.join(intrinsic_path,  f'{intrinsic_xml}'),
                                         flags=cv2.FILE_STORAGE_READ)

    #取得给定的相机内参
    cameraMatrix, distCoeffs = fp_calibration.getNode('camera_matrix').mat(), fp_calibration.getNode(
            'distortion_coefficients').mat()

    fp_calibration.release()
    fp_calibration = cv2.FileStorage(os.path.join(extrinsic_path,f'{extrinsic_xml}')  ,
                                         flags=cv2.FILE_STORAGE_READ)
    rvec, tvec = fp_calibration.getNode('rvec').mat().squeeze(), fp_calibration.getNode('tvec').mat().squeeze()
    #取得给定的相机外参
    fp_calibration.release()

    return  rvec, tvec, cameraMatrix, distCoeffs

def map_point_to_world_on_plane(r, t, c, d, u, v, plane_origin, plane_normal = [0, -1, 0]):
    # Undistort the image coordinates
    undistorted_points = cv2.undistortPoints(np.array([[[u, v]]], dtype=np.float32), c, d)

    # Create homogeneous image coordinates
    homogeneous_image_point = np.array([undistorted_points[0][0][0], undistorted_points[0][0][1], 1])

    # Calculate the rotation matrix
    rotation_matrix, _ = cv2.Rodrigues(r)

    # Transform the image point to a ray in world coordinates
    ray_direction = np.dot(rotation_matrix.T, homogeneous_image_point)

    # The origin of the ray is the camera position in world coordinates
    ray_origin = -np.dot(rotation_matrix.T, t)

    # Find the intersection of the ray and the plane
    normal_dot_ray_direction = np.dot(plane_normal, ray_direction)

    if abs(normal_dot_ray_direction) < 1e-6:
        raise Exception("The ray is parallel to the plane.")

    t0 = np.dot(plane_normal, plane_origin - ray_origin) / normal_dot_ray_direction
    intersection_point = ray_origin + t0 * ray_direction

    return intersection_point

def get_camera_position(r,t):
    # Calculate the inverse rotation matrix
    rotation_matrix, _ = cv2.Rodrigues(r)
    inv_rotation_matrix = np.linalg.inv(rotation_matrix)

    # Calculate the camera position
    inv_camera_position = -np.dot(inv_rotation_matrix, t)

    return inv_camera_position
