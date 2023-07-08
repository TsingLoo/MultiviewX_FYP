import os

import cv2

import json

import shutil
import random

import numpy as np

import math

import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d import Axes3D

from PIL import Image, ImageDraw

from math import sqrt

from unitConversion import *

from datasetParameters import *

from shapely.geometry import Point, Polygon

from shapely.geometry import mapping


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

            print(f'{(projected_point_2d - corner)<[0.00005,0.00005]}  Original point: {corner} WorldPoint: {worldpoint}')




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




def draw_views():
    fig, ax = plt.subplots()
    json_file = 'viewarea.json'
    # Load the dictionary from the JSON file
    with open(json_file, 'r') as file:
        json_dict = json.load(file)

    # Draw the AOICorners2D
    AOICorners2D = json_dict['AOICorners2D']
    AOICorners2D.append(AOICorners2D[0]) # repeat the first point to create a 'closed loop'
    xs, ys = zip(*AOICorners2D) # create lists of x and y values
    plt.plot(xs, ys, 'r-') # 'r-' is the color red

    # Draw the polygons from viewarea_dict
    for key, cam_dict in json_dict.items():
        if key == 'AOICorners2D': continue # skip the AOICorners2D entry

        points = cam_dict['viewarea_corners']
        points.append(points[0]) # repeat the first point to create a 'closed loop'
        xs, ys = zip(*points) # create lists of x and y values
        plt.plot(xs, ys, label=key)
        plt.text(points[0][0],points[0][1] , 'lt', color='blue')
        plt.text(points[1][0],points[1][1] , 'rt', color='blue')
        plt.text(points[2][0],points[2][1] , 'rb', color='blue')
        plt.text(points[3][0],points[3][1] , 'lb', color='blue')

        # Mark the camera position
        camera_position = cam_dict['camera_position']
        print(f'{key} : {camera_position}')
        plt.scatter(camera_position[0], camera_position[1], c='blue', marker='x') # we choose x and z position for 2D plot
        plt.text(camera_position[0], camera_position[1], key, color='blue')

    ax.set_aspect('equal', adjustable='box')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('AOI and Viewarea of cams')
    ax.set_xticks(np.arange(0, np.ceil(ax.get_xlim()[1]), step=1))  # Setting grid
    ax.set_yticks(np.arange(0, np.ceil(ax.get_ylim()[1]), step=1))
    plt.grid(True)
    plt.legend()

    # Show the plot
    #plt.show()
    plt.savefig('viewarea.png')
    shutil.move(json_file, datasetParameters.DATASET_NAME)
    

    

if __name__ == '__main__':
    a()