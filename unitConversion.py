import numpy as np
import os
import cv2
import re
import datasetParameters
from datasetParameters import *
import xml.etree.ElementTree as ET

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


def get_calibration_files(calibration_path, camIdx):
    intrinsic_path = os.path.join(calibration_path, 'intrinsic')
    extrinsic_path = os.path.join(calibration_path, 'extrinsic')

    # List files in the intrinsic and extrinsic directories
    intrinsic_files = os.listdir(intrinsic_path)
    extrinsic_files = os.listdir(extrinsic_path)

    # Collect and pair the files
    calibration_pairs = []
    for intr_file in intrinsic_files:
        match = re.match(r'intr_(\w+).xml', intr_file)
        if match:
            file_id = match.group(1)
            extr_file = f'extr_{file_id}.xml'
            if extr_file in extrinsic_files:
                calibration_pairs.append((intr_file, extr_file))

    # Sort the pairs to ensure consistent ordering
    calibration_pairs.sort()

    if camIdx < len(calibration_pairs):
        return calibration_pairs[camIdx]
    else:
        return None, None

def get_calibration(camIdx, DATASET_NAME=""):
    if DATASET_NAME == "":
        DATASET_NAME = datasetParameters.DATASET_NAME

    calibration_path = os.path.join(DATASET_NAME, "calibrations")

    # Get the calibration file names
    intrinsic_xml, extrinsic_xml = get_calibration_files(calibration_path, camIdx)
    if not intrinsic_xml or not extrinsic_xml:
        raise FileNotFoundError("Matching intrinsic and extrinsic files not found for the given camera index.")

    print(os.path.join(calibration_path, 'intrinsic', intrinsic_xml))

    fp_calibration = cv2.FileStorage(os.path.join(calibration_path, 'intrinsic', intrinsic_xml),
                                     flags=cv2.FILE_STORAGE_READ)
    cameraMatrix, distCoeffs = fp_calibration.getNode('camera_matrix').mat(), fp_calibration.getNode(
        'distortion_coefficients').mat()
    fp_calibration.release()


    try:
        print(os.path.join(calibration_path, 'extrinsic', extrinsic_xml))

        fp_calibration = cv2.FileStorage(os.path.join(calibration_path, 'extrinsic', extrinsic_xml),
                                     flags=cv2.FILE_STORAGE_READ)
        rvec, tvec = fp_calibration.getNode('rvec').mat().squeeze(), fp_calibration.getNode('tvec').mat().squeeze()
        fp_calibration.release()
    except:
        # Parse the XML file
        tree = ET.parse(os.path.join(os.path.join(calibration_path, 'extrinsic'), extrinsic_xml))
        root = tree.getroot()

        # Extract and convert the rotation vector (rvec)
        rvec_text = root.find('rvec').text.strip()
        rvec = np.array([float(num) for num in rvec_text.split()])

        # Extract and convert the translation vector (tvec)
        tvec_text = root.find('tvec').text.strip()
        tvec = np.array([float(num) for num in tvec_text.split()])


    tvec = tvec * OverlapUnitConvert

    return rvec, tvec, cameraMatrix, distCoeffs

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

    offset = np.array(OverlapGridOffset)
    inv_camera_position = inv_camera_position + offset



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

def calculate_intersection(p1, p2, edge):
    """
    Calculate the intersection of a line segment (p1, p2) with another line segment (edge).
    Assumes that all points are 2D.
    """
    #print(f"{p1} {p2}")

    # Convert points to numpy arrays
    p1, p2 = np.array(p1, dtype=np.float64), np.array(p2, dtype=np.float64)
    edge = np.array(edge, dtype=np.float64)

    p1[2] = 0
    p2[2] = 0

    # Line equation for p1p2: A1x + B1y = C1
    A1 = p2[1] - p1[1]
    B1 = p1[0] - p2[0]
    C1 = A1 * p1[0] + B1 * p1[1]

    #print()

    #print(f"L1: {A1}x + {B1}y = {C1}")

    #print(edge)

    # Line equation for edge: A2x + B2y = C2
    A2 = edge[1,1] - edge[0,1]
    B2 = edge[0,0] - edge[1,0]
    C2 = A2 * edge[0,0] + B2 * edge[0,1]

    #print(f"L2: {A2}x + {B2}Y = {C2}")

    # Solve the system of equations
    determinant = A1 * B2 - A2 * B1
    if determinant == 0:
        return None  # Lines are parallel

    x = (B2 * C1 - B1 * C2) / determinant
    y = (A1 * C2 - A2 * C1) / determinant

    #print(f"The possible point is {[x, y, 0]}")

    epsilon = 1e-5  # Tolerance value, can be adjusted based on the precision you need

    # Use the tolerance in comparisons
    if (min(p1[0], p2[0]) - epsilon <= x <= max(p1[0], p2[0]) + epsilon and
            min(p1[1], p2[1]) - epsilon <= y <= max(p1[1], p2[1]) + epsilon and
            min(edge[0, 0], edge[1, 0]) - epsilon <= x <= max(edge[0, 0], edge[1, 0]) + epsilon and
            min(edge[0, 1], edge[1, 1]) - epsilon <= y <= max(edge[0, 1], edge[1, 1]) + epsilon):

        #print([x, y, 0])
        return np.array([x, y, 0])
    else:
        return None