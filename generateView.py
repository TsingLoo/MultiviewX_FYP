import os
import cv2
import json
import shutil
import random
import numpy as np
import math
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from PIL import Image, ImageDraw
from math import sqrt
from unitConversion import *
from datasetParameters import *


AOICorners2D = [[0, 0],

            [0 + MAP_WIDTH, 0], 

            [0 + MAP_WIDTH, 0 + MAP_HEIGHT], 

            [0, 0 + MAP_HEIGHT]]
json_dict = {} 


def generate_View():
    IMAGE_ORIGIN = [0,0]

    ImageCorners = [IMAGE_ORIGIN,

                    [IMAGE_ORIGIN[0] + IMAGE_WIDTH, IMAGE_ORIGIN[1]], 

                    [IMAGE_ORIGIN[0] + IMAGE_WIDTH, IMAGE_ORIGIN[1] + IMAGE_HEIGHT],

                    [IMAGE_ORIGIN[0], IMAGE_ORIGIN[1] + IMAGE_HEIGHT]]



    for i in range(NUM_CAM):

        rvec, tvec, cameraMatrix, distCoeffs = get_calibration(i)   

        cam_pos = get_camera_position(rvec,tvec)
        
        #polygon = Polygon(AOICorners2D)


        viewarea_corners_2d = []


        for corner in ImageCorners:

            worldpoint =  map_point_to_world_on_plane(rvec,tvec,cameraMatrix,distCoeffs, corner[0], corner[1], GRID_ORIGIN)

            worldpoint2D = [worldpoint[0], worldpoint[2]]

            viewarea_corners_2d.append(worldpoint2D)

            projected_point_2d, _ = cv2.projectPoints(worldpoint, rvec, tvec, cameraMatrix, distCoeffs)

            print(f'{(projected_point_2d - corner)<[0.0001,0.0001]}  Original point: {corner} WorldPoint: {worldpoint}')




            # if(worldpoint2D[0] >= 0 and worldpoint2D[1] >= 0):

            #     print(f'cam{i + 1} receives a new point: {worldpoint2D}')

            #     if point_in_polygon(worldpoint2D, polygon):

            #         # Update the polygon


            #         polygon = update_polygon(polygon, worldpoint2D)

        print(cam_pos)

        json_dict[f'cam{i + 1}'] = {'camera_position': cam_pos, 'viewarea_corners': viewarea_corners_2d}
        json_dict['AOICorners2D'] = AOICorners2D

        # polygons[f'cam{i + 1}'] = polygon

        # # Convert the Polygon object to GeoJSON format

        # geojson_polygon = mapping(polygon)

        # polygons_dict[f'cam{i + 1}'] = geojson_polygon

        # print(f'The final polygon of the view {i + 1} is {polygon}')
        print()
        

    json_file = 'viewarea.json'

    # Save the dictionary to a JSON file

    with open(json_file, 'w') as file:
        json.dump(json_dict, file)
               

    


def point_in_polygon(point, polygon):
    p1 = Point(point)
    p2 = Polygon(polygon)
    return p1.within(p2)


def ccw_sort(points):
    center = [sum([p[0] for p in points])/len(points), sum([p[1] for p in points])/len(points)]
    points.sort(key=lambda p: math.atan2(p[1] - center[1],
                                         p[0] - center[0]))
    return points

def calculate_angle(p1, p2):
    return math.atan2(p2[1] - p1[1], p2[0] - p1[0])

def draw_views():
    fig, ax = plt.subplots()
    json_file = 'viewarea.json'
    
    # Load the dictionary from the JSON file
    with open(json_file, 'r') as file:
        json_dict = json.load(file)

    # Define the AOICorners2D
    AOICorners2D = json_dict['AOICorners2D']
    AOICorners2D.append(AOICorners2D[0]) # repeat the first point to create a 'closed loop'
    AOI_polygon = Polygon(AOICorners2D)

    # Draw the AOICorners2D
    xs, ys = zip(*AOICorners2D) # create lists of x and y values
    plt.plot(xs, ys, 'r-', label='AOI') # 'r-' is the color red

    # Prepare a colormap
    cmap = plt.get_cmap('tab10')

    # Draw the polygons from viewarea_dict
    for idx, (key, cam_dict) in enumerate(json_dict.items()):
        if key == 'AOICorners2D': continue 

        points = cam_dict['viewarea_corners']
        points.append(points[0])

        camera_position = cam_dict['camera_position']
        plt.scatter(camera_position[0], camera_position[1], c=cmap(idx % cmap.N), marker='x')
        plt.text(camera_position[0], camera_position[1], key, color=cmap(idx % cmap.N))

        # Define the polygons
        points = ccw_sort(points)
        camera_polygon = Polygon(points)

        # Check if the polygons intersect and draw the intersection
        if camera_polygon.intersects(AOI_polygon):
            intersection = camera_polygon.intersection(AOI_polygon)
            xs, ys = intersection.exterior.xy
            plt.fill(xs, ys, alpha=0.5, fc=cmap(idx % cmap.N), label=f'Intersection {key}')

            # Create a list of points with their corresponding angles
            points_with_angles = [(point, calculate_angle(camera_position, point)) for point in intersection.exterior.coords[:-1]]
            points_with_angles.sort(key=lambda x: x[1])  # sort by angle

            # Draw lines from the camera to the boundaries of the intersection (FOV lines)
            for point, _ in [points_with_angles[0], points_with_angles[-1]]:  # get the points with the smallest and largest angle
                plt.plot([camera_position[0], point[0]], [camera_position[1], point[1]], color=cmap(idx % cmap.N), linestyle='--')

    ax.set_aspect('equal', adjustable='box')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Overlap between AOI and Viewarea of cams')
    ax.set_xticks(np.arange(0, np.ceil(ax.get_xlim()[1]), step=1))  # Setting grid
    ax.set_yticks(np.arange(0, np.ceil(ax.get_ylim()[1]), step=1))
    plt.grid(True)
    plt.legend()

    # Save the plot as SVG
    plt.savefig('overlap_viewarea.svg', format='svg')  # save as SVG file
    shutil.move(json_file, datasetParameters.DATASET_NAME)



    

if __name__ == '__main__':
    a()