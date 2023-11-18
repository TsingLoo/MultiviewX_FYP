import cv2
import numpy as np
import matplotlib.pyplot as plt
from datasetParameters import *
from unitConversion import *
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def generateView():
    for i in range(NUM_CAM):

        generateOneCameraView(i)


def generateOneCameraView(idx):

    print()
    print(f"Now generating view for Camera {idx + 1}")

    # Camera intrinsic parameters
    rvec, tvec, camera_matrix, _ = get_calibration(idx)

    print(f"Camera {idx + 1}'s posistion is {get_camera_position(rvec, tvec)}")

    # Convert rotation vector to rotation matrix
    R, _ = cv2.Rodrigues(rvec)

    # Define near and far planes
    near, far = 0.1, 1000

    # Frustum corners in camera coordinates
    h, w = camera_matrix[1, 2] * 2, camera_matrix[0, 2] * 2
    frustum_corners = np.array([
        [0, 0, near], [w, 0, near], [w, h, near], [0, h, near],  # near plane
        [0, 0, far], [w, 0, far], [w, h, far], [0, h, far]       # far plane
    ])

    # Transform frustum corners to world coordinates
    world_corners = []
    for corner in frustum_corners:
        # Convert to normalized device coordinates
        ndc = np.dot(np.linalg.inv(camera_matrix), np.append(corner[:2], 1)) * corner[2]
        # Transform to world coordinates
        world_corner = np.dot(np.linalg.inv(R), ndc - tvec.squeeze())
        world_corners.append(world_corner)

    world_corners = np.array(world_corners)

    #print(world_corners)

    # Plotting the frustum
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot the points
    x, y, z = world_corners[:, 0], world_corners[:, 1], world_corners[:, 2]
    ax.scatter(x, y, z)

    # Connect corresponding near and far plane corners
    for i in range(4):
        if i == 1 or i == 2:
            ax.plot([world_corners[i][0], world_corners[i+4][0]],
                [world_corners[i][1], world_corners[i+4][1]],
                [world_corners[i][2], world_corners[i+4][2]], 'r')

    for i in range(4):
        if i == 0 or i == 3:
            ax.plot([world_corners[i][0], world_corners[i+4][0]],
                [world_corners[i][1], world_corners[i+4][1]],
                [world_corners[i][2], world_corners[i+4][2]], 'r')


    # Calculate intersections for the specified lines
    intersections = []
    for i in range(2, 4):
        intersection = intersection_with_ground(world_corners[i], world_corners[i+4])
        if intersection is not None:
            intersections.append(intersection)

    # Add intersection points to the plot
    for point in intersections:
        print(f"Green points is {point} ")
        ax.scatter([point[0]], [point[1]], [point[2]], color='green', s=50)


    # Define the corners of the AOI rectangle
    aoi_corners = np.array([
        [0, 0, 0],  # Origin
        [MAP_WIDTH, 0, 0],
        [MAP_WIDTH, MAP_HEIGHT, 0],
        [0, MAP_HEIGHT, 0],
        [0, 0, 0]  # Close the rectangle
    ])

    aoi_points = [
        [0, 0, 0],
        [MAP_WIDTH, 0, 0],
        [MAP_WIDTH, MAP_HEIGHT, 0],
        [0, MAP_HEIGHT, 0]
        # Add any additional points on the edges if needed
    ]

    # Define lines for each edge of the AOI
    aoi_edges = [
        (np.array([0, 0, 0]), np.array([1, 0, 0])),  # Bottom edge (along X-axis)
        (np.array([MAP_WIDTH, 0, 0]), np.array([0, 1, 0])),  # Right edge (along Y-axis)
        (np.array([MAP_WIDTH, MAP_HEIGHT, 0]), np.array([-1, 0, 0])),  # Top edge (opposite to bottom)
        (np.array([0, MAP_HEIGHT, 0]), np.array([0, -1, 0]))  # Left edge (opposite to right)
    ]


    # Plot the AOI on the ground
    ax.plot(aoi_corners[:, 0], aoi_corners[:, 1], aoi_corners[:, 2], color='purple', label='AOI')


    # Define the first plane using two lines from the frustum
    plane1 = find_plane_equation(world_corners[1], world_corners[5], world_corners[2])

    # Define the second plane using two other lines from the frustum
    plane2 = find_plane_equation(world_corners[0], world_corners[4], world_corners[3])




    intersection_points_with_aoi_edges = []

    # Find and plot the intersections for both planes
    for plane in [plane1, plane2]:
        for i, (line_point, line_dir) in enumerate(aoi_edges):
            intersection_point = intersection_line_plane(plane, line_point, line_dir)
            if intersection_point is not None:
                intersection_points_with_aoi_edges.append(intersection_point)
                print(f"Intersection with AOI Edge {i} and Plane: {intersection_point}")
                ax.scatter([intersection_point[0]], [intersection_point[1]], [intersection_point[2]], color='orange', s=100)

    # Calculate the camera position
    camera_position = get_camera_position(rvec, tvec)
    camera_direction = -np.dot(np.linalg.inv(cv2.Rodrigues(rvec)[0]), np.array([0, 0, -1]))

    # Length of the direction vector for visualization
    direction_length = 10  # Adjust as needed

    # End point of the direction vector
    direction_end_point = camera_position + direction_length * camera_direction

    # Camera's projection on the ground
    camera_projection_on_ground = (camera_position[0], camera_position[1], 0)


    #print(is_point_in_frustum( (25, 16, 0)  , world_corners))

    # Image dimensions (width and height)
    image_width = IMAGE_WIDTH  # Replace with your image width
    image_height = IMAGE_HEIGHT  # Replace with your image height

    # Focal lengths
    f_x = camera_matrix[0, 0]
    f_y = camera_matrix[1, 1]

    # Calculate horizontal and vertical FoV in degrees
    h_fov = 2 * np.degrees(np.arctan(image_width / (2 * f_x)))
    v_fov = 2 * np.degrees(np.arctan(image_height / (2 * f_y)))

    print(f"Horizontal FoV: {h_fov} degrees")
    print(f"Vertical FoV: {v_fov} degrees")


    # Plotting the camera position and its projection
    ax.scatter(*camera_position, color='blue', s=5, label='Camera Position')
    # Plot the camera direction
    ax.quiver(*camera_position, *camera_direction, length=direction_length, color='red', arrow_length_ratio=0.1, label='Camera Direction')
    ax.scatter(*camera_projection_on_ground, color='cyan', s=100, label='Camera Projection on Ground')


    # Assuming 'intersections' and 'intersection_points_with_aoi_edges' are lists of NumPy arrays
    all_points = intersections

    # Convert 'camera_projection_on_ground' to a NumPy array if it's not already
    camera_projection_on_ground_array = np.array(camera_projection_on_ground)


    all_points.append(camera_projection_on_ground_array)

    # Extend 'all_points' with 'intersection_points_with_aoi_edges'
    all_points.extend(intersection_points_with_aoi_edges)

    all_points.extend(aoi_points)

    # Ensure all elements in 'all_points' are NumPy arrays
    all_points = [np.array(point) for point in all_points]

    #print("all_points")
    #print(all_points)

    print(f"All point is {all_points}")

    # Filter points to include only those within or on the edges of the AOI
    filtered_points = [point for point in all_points if (is_point_in_aoi(point, MAP_WIDTH, MAP_HEIGHT))]

    print(f"AOI Filtered points are {filtered_points}")

    filtered_points = [point for point in filtered_points if (is_point_in_frustum(point, world_corners))]

    print(f"Final Filtered points are {filtered_points}")



    # Assuming 'aoi_corners' and 'filtered_points' are already defined in your code
    # 'aoi_corners' are the corners of the AOI
    # 'filtered_points' are the points within or on the edges of the AOI


    #print(filtered_points)

    # # Combine and sort the points to form the overlap area
    overlap_points = np.vstack(( filtered_points))  # Exclude the last point in aoi_corners as it's the same as the first
    overlap_points = sort_points_clockwise(overlap_points)

    #print( overlap_points)

    #print(overlap_points)


    # [Your existing code for plotting frustum, camera position, etc.]
     #Plot the overlap area
    overlap_poly = Poly3DCollection([overlap_points], color='green', alpha=0.5)
    ax.add_collection3d(overlap_poly)
    # [Rest of your plotting code]



    # Set plot limits
    max_limit = max(MAP_WIDTH, MAP_HEIGHT)
    ax.set_xlim([0, max_limit])
    ax.set_ylim([0, max_limit])
    ax.set_zlim([0, max_limit])

    # Set the aspect of the plot to be equal
    ax.set_box_aspect([1,1,1])  # Equal aspect ratio

    # Create a grid
    ax.grid(True)
    ax.xaxis._axinfo["grid"].update(color = 'gray', linestyle = '--')
    ax.yaxis._axinfo["grid"].update(color = 'gray', linestyle = '--')
    ax.zaxis._axinfo["grid"].update(color = 'gray', linestyle = '--')

    # Setting labels
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')

    # Legend
    ax.legend()

    # Show plot
    plt.show()
