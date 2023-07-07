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

polygons = {}
def generate_View():
    polygons_dict = {}    
    IMAGE_ORIGIN = [0,0]
    
    ImageCorners = [IMAGE_ORIGIN,
                    [IMAGE_ORIGIN[0] + IMAGE_WIDTH, IMAGE_ORIGIN[1]], 
                    [IMAGE_ORIGIN[0] + IMAGE_WIDTH, IMAGE_ORIGIN[1] + IMAGE_HEIGHT],
                    [IMAGE_ORIGIN[0], IMAGE_ORIGIN[1] + IMAGE_HEIGHT]]
    
    AOICorners = [GRID_ORIGIN,
              [GRID_ORIGIN[0] + MAP_WIDTH, GRID_ORIGIN[1], GRID_ORIGIN[2]], 
              [GRID_ORIGIN[0] + MAP_WIDTH, GRID_ORIGIN[1], GRID_ORIGIN[2] + MAP_HEIGHT], 
              [GRID_ORIGIN[0], GRID_ORIGIN[1], GRID_ORIGIN[2] + MAP_HEIGHT]]

    AOICorners2D = [[0, 0],
              [0 + MAP_WIDTH, 0], 
              [0 + MAP_WIDTH, 0 + MAP_HEIGHT], 
              [0, 0 + MAP_HEIGHT]]

    for i in range(NUM_CAM):
        rvec, tvec, cameraMatrix, distCoeffs = get_calibration(i)   

        cam_pos = get_camera_position(rvec,tvec)
        AOICorners2D.append([cam_pos[0],cam_pos[2]])
        polygon = Polygon(AOICorners2D)

        for corner in ImageCorners:
            worldpoint =  map_point_to_world_on_plane(rvec,tvec,cameraMatrix,distCoeffs, corner[0], corner[1], GRID_ORIGIN)
            worldpoint2D = [worldpoint[0], worldpoint[2]]
            projected_point_2d, _ = cv2.projectPoints(worldpoint, rvec, tvec, cameraMatrix, distCoeffs)
            print(f'{(projected_point_2d - corner)<[0.00005,0.00005]}  Original point: {corner} WorldPoint: {worldpoint}')
            if(worldpoint2D[0] >= 0 and worldpoint2D[1] >= 0):
                print(f'cam{i + 1} receives a new point: {worldpoint2D}')
                if point_in_polygon(worldpoint2D, polygon):
                    # Update the polygon

                    polygon = update_polygon(polygon, worldpoint2D)

        polygons[f'cam{i + 1}'] = polygon
        # Convert the Polygon object to GeoJSON format
        geojson_polygon = mapping(polygon)
        polygons_dict[f'cam{i + 1}'] = geojson_polygon
        print(f'The final polygon of the view {i + 1} is {polygon}')
        print()
        
    json_file = 'polygons.json'
    # Save the dictionary to a JSON file
    with open(json_file, 'w') as file:
        json.dump(polygons_dict, file)
               
    shutil.move(json_file, datasetParameters.DATASET_NAME)
    

    

def point_in_polygon(point, polygon):
    p1 = Point(point)
    p2 = Polygon(polygon)
    return p1.within(p2)

def distance(edge, point):
    """Calculate the shortest distance between a point and a line segment."""
    # Line segment endpoints
    x1, y1 = edge[0]
    x2, y2 = edge[1]

    # Point coordinates
    x3, y3 = point

    # Calculate distances between points
    px = x2 - x1
    py = y2 - y1
    something = px*px + py*py
    u =  ((x3 - x1) * px + (y3 - y1) * py) / float(something)

    # Check for endpoints
    if u > 1:
        u = 1
    elif u < 0:
        u = 0

    # Calculate shortest distance
    x = x1 + u * px
    y = y1 + u * py
    dx = x - x3
    dy = y - y3

    return sqrt(dx*dx + dy*dy)

def update_polygon(polygon, point):
    # Get the coordinates of the polygon
    coords = list(polygon.exterior.coords)

    # Calculate the distance from the point to each edge of the polygon
    distances = [distance(edge, point) for edge in zip(coords[:-1], coords[1:])]

    # Find the edge with the smallest distance
    closest_edge_index = distances.index(min(distances))

    # Get the vertices of the closest edge
    v1, v2 = coords[closest_edge_index], coords[closest_edge_index + 1]

    # Remove the closest edge from the polygon by excluding one of its vertices
    new_coords = coords[:closest_edge_index + 1] + coords[closest_edge_index + 2:]

    # Insert the point into the list of coordinates at the correct position
    new_coords.insert(closest_edge_index + 1, point)

    # Create and return a new polygon
    new_polygon = Polygon(new_coords)
    return new_polygon

def draw_views():
    width, height = MAP_WIDTH* 20, MAP_HEIGHT*20
    image = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    for key, polygon in polygons.items():
        
        max_x = max(y for _, y in polygon.exterior.coords for polygon in polygons.values())
        max_y = max(x for x, _ in polygon.exterior.coords for polygon in polygons.values())
        
        # Extract the coordinates of the polygon
        coordinates = list(mapping(polygon)["coordinates"][0])
        print(f"draw polygon for {coordinates}")
        # Convert the coordinates to fit within the image size
        normalized_vertices = [(x / max_x * width, y / max_y * height) for x, y in coordinates]
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.polygon(normalized_vertices, outline= color)
    image.show()
    print()

    
if __name__ == '__main__':
    a()