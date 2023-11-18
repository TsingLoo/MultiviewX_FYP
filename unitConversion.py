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
    # print(r)
    # print(t)

    rotation_matrix, _ = cv2.Rodrigues(r)
    inv_rotation_matrix = np.linalg.inv(rotation_matrix)

    # Calculate the camera position
    inv_camera_position = -np.dot(inv_rotation_matrix, t)

    return inv_camera_position.tolist()

# Function to find plane equation
def find_plane_equation(p1, p2, p3):
    # Vectors in the plane
    v1 = p3 - p1
    v2 = p2 - p1

    # Normal vector to the plane
    normal = np.cross(v1, v2)

    # Plane equation: Ax + By + Cz + D = 0
    A, B, C = normal
    D = -np.dot(normal, p1)
    return A, B, C, D

def is_point_in_aoi(point, aoi_width, aoi_height):
    x, y, z = point
    isInAOI = 0 <= x <= aoi_width and 0 <= y <= aoi_height and -0.005 <= z <= 0.005
    if(not isInAOI):
        print(f'Point {point} is not in AOI')
    return isInAOI


# Function to find intersection of a line with a plane
def intersection_line_plane(plane, line_point, line_dir):
    A, B, C, D = plane
    x0, y0, z0 = line_point
    l, m, n = line_dir

    # Check if the line is parallel to the plane
    if A*l + B*m + C*n == 0:
        return None  # No intersection, the line is parallel to the plane

    # Find the parameter t for the line
    t = -(A*x0 + B*y0 + C*z0 + D) / (A*l + B*m + C*n)

    # Find the intersection point
    intersection = line_point + t * line_dir
    return intersection



def is_point_on_correct_side_of_plane(point, p1, p2, p3):
    """
    Check if a point is on the correct side of a plane defined by three points.

    :param point: The point to check.
    :param p1, p2, p3: Points defining the plane.
    :return: True if the point is on the correct side, False otherwise.
    """
    normal = -np.cross(p2 - p1, p3 - p1)
    result = np.dot(normal, point - p1) >= - 1
    #print(f"Is correct side of the plane {p1,p2,p3}:", result)

    return result, np.dot(normal, point - p1)

def is_point_in_frustum(point, frustum_corners):
    """
    Check if a point is inside the camera's view frustum.

    :param point: The point to check, in world coordinates.
    :param frustum_corners: The corners of the frustum in world coordinates.
    :return: True if the point is inside the frustum, False otherwise.
    """

    # Define the six planes of the frustum with descriptive names
    planes = {
        'Near Plane': (frustum_corners[0], frustum_corners[1], frustum_corners[5]),
        'Far Plane': (frustum_corners[2], frustum_corners[3], frustum_corners[7]),
        'Left Plane': (frustum_corners[1], frustum_corners[0], frustum_corners[2]),
        'Right Plane': (frustum_corners[4], frustum_corners[5], frustum_corners[6]),
        'Bottom Plane': (frustum_corners[3], frustum_corners[0], frustum_corners[4]),
        'Top Plane': (frustum_corners[1], frustum_corners[2], frustum_corners[6])
    }

    for plane_name, plane_points in planes.items():
        isOnCorrectSide, value = is_point_on_correct_side_of_plane(point, *plane_points)

        if not isOnCorrectSide:
            print(f"{point} is not in the frustum because it failed at the {plane_name} (plane points: {plane_points}), value: {value}")
            return False

    print(f"{point} is in the frustum")
    return True

# Function to sort points in clockwise order (assuming they are all in the same plane)
def sort_points_clockwise(points):
    center = np.mean(points, axis=0)
    sorted_points = sorted(points, key=lambda point: np.arctan2(point[1] - center[1], point[0] - center[0]))
    return np.array(sorted_points)

def intersection_with_ground(corner_near, corner_far):
    # Line direction vector
    direction = corner_far - corner_near

    # Assuming corner_near is not already on the ground
    if direction[2] == 0:
        return None  # Line is parallel to the ground

    # Find the parameter t at which the line intersects the ground
    t = -corner_near[2] / direction[2]

    # Calculate the intersection point
    intersection = corner_near + t * direction

    return intersection