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

VIEW_DISTANCE = 8
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
        

    #json_file = 'viewarea.json'

    # Save the dictionary to a JSON file

    #with open(json_file, 'w') as file:
        #json.dump(json_dict, file)
               

    


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

    AOICorners2D = [[0, 0], [0 + MAP_WIDTH, 0], [0 + MAP_WIDTH, 0 + MAP_HEIGHT], [0, 0 + MAP_HEIGHT]]
    AOICorners2D.append(AOICorners2D[0]) 
    xs, ys = zip(*AOICorners2D)
    plt.plot(xs, ys, 'r-')

    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    for idx in range(NUM_CAM):
        rvec, tvec, cameraMatrix, _ = get_calibration(idx)
        camera_position = get_camera_position(rvec, tvec)
        camera_position = camera_position[:2]
        fov_x = 2 * np.arctan(IMAGE_WIDTH / (2 * cameraMatrix[0, 0]))

        # Calculate rotation matrix and find pan angle
        R, _ = cv2.Rodrigues(rvec)
        pan_angle = np.arctan2(R[1, 0], R[0, 0]) + np.pi/2  # adjust angle by subtracting 90 degrees

        # Calculate points on the edge of the FOV
        fov_angles = np.linspace(-fov_x / 2, fov_x / 2, 30)
        fov_points = VIEW_DISTANCE * np.array([np.cos(fov_angles + pan_angle), np.sin(fov_angles + pan_angle)]).T + camera_position

        # Append camera position as the first and last points
        fov_points = np.concatenate(([camera_position], fov_points, [camera_position]), axis=0)
        
        xs, ys = zip(*fov_points)
        plt.fill(xs, ys, color=colors[idx % len(colors)], alpha=0.3)  # Fill FOV area with color

        plt.scatter(*camera_position, c=colors[idx % len(colors)], marker='x')
        plt.text(*camera_position, 'cam' + str(idx), color=colors[idx % len(colors)])

    ax.set_aspect('equal', adjustable='box')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('AOI and FOVs of cameras')
    ax.set_xticks(np.arange(0, np.ceil(ax.get_xlim()[1]), step=1))
    ax.set_yticks(np.arange(0, np.ceil(ax.get_ylim()[1]), step=1))
    plt.grid(True)

    plt.savefig('FOVs.svg')




if __name__ == '__main__':
    a()