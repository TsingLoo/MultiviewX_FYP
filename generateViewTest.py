import cv2
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def get_camera_position(r, t):
    # Calculate the inverse rotation matrix
    rotation_matrix, _ = cv2.Rodrigues(r)
    inv_rotation_matrix = np.linalg.inv(rotation_matrix)

    # Calculate the camera position
    inv_camera_position = -np.dot(inv_rotation_matrix, t)

    return inv_camera_position.tolist()

# Camera intrinsic parameters
camera_matrix = np.array([[623.53826751886811, 0, 639.99822858598884],
                          [0, 623.53879058816437, 360.00054487907948],
                          [0, 0, 1]])

# Rotation vector and translation vector
rvec = np.array([[1.2867339887546156], [1.2867436957687048], [-1.1572848445327359]])
tvec = np.array([[-5.4297286529463840], [-1.4755107733008084], [30.927228994180467]])

print(get_camera_position(rvec, tvec))

# Convert rotation vector to rotation matrix
R, _ = cv2.Rodrigues(rvec)

# Define near and far planes
near, far = 0.0001, 1

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

# Function to calculate intersection with ground plane
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

# Calculate intersections for the specified lines
intersections = []
for i in range(2, 4):
    intersection = intersection_with_ground(world_corners[i], world_corners[i+4])
    if intersection is not None:
        intersections.append(intersection)

# Add intersection points to the plot
for point in intersections:
    ax.scatter([point[0]], [point[1]], [point[2]], color='green', s=50)

# Define the AOI dimensions
aoi_width = 25
aoi_height = 16

# Define the corners of the AOI rectangle
aoi_corners = np.array([
    [0, 0, 0],  # Origin
    [aoi_width, 0, 0],
    [aoi_width, aoi_height, 0],
    [0, aoi_height, 0],
    [0, 0, 0]  # Close the rectangle
])

# Plot the AOI on the ground
ax.plot(aoi_corners[:, 0], aoi_corners[:, 1], aoi_corners[:, 2], color='purple', label='AOI')

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

# Define the first plane using two lines from the frustum
plane1 = find_plane_equation(world_corners[1], world_corners[5], world_corners[2])

# Define the second plane using two other lines from the frustum
plane2 = find_plane_equation(world_corners[0], world_corners[4], world_corners[3])

# Define lines for each edge of the AOI
aoi_edges = [
    (np.array([0, 0, 0]), np.array([1, 0, 0])),  # Bottom edge (along X-axis)
    (np.array([aoi_width, 0, 0]), np.array([0, 1, 0])),  # Right edge (along Y-axis)
    (np.array([aoi_width, aoi_height, 0]), np.array([-1, 0, 0])),  # Top edge (opposite to bottom)
    (np.array([0, aoi_height, 0]), np.array([0, -1, 0]))  # Left edge (opposite to right)
]


# Find and plot the intersections for both planes
for plane in [plane1, plane2]:
    for i, (line_point, line_dir) in enumerate(aoi_edges):
        intersection_point = intersection_line_plane(plane, line_point, line_dir)
        if intersection_point is not None:
            print(f"Intersection with AOI Edge {i} and Plane: {intersection_point}")
            ax.scatter([intersection_point[0]], [intersection_point[1]], [intersection_point[2]], color='orange', s=100)

# Calculate the camera position
camera_position = get_camera_position(rvec, tvec)

# Camera's projection on the ground
camera_projection_on_ground = [camera_position[0], camera_position[1], 0]

# Plotting the camera position and its projection
ax.scatter(*camera_position, color='blue', s=5, label='Camera Position')
ax.scatter(*camera_projection_on_ground, color='cyan', s=100, label='Camera Projection on Ground')





# Set plot limits
max_limit = max(aoi_width, aoi_height)
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
