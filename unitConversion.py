from datasetParameters import *
import numpy as np


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

def get_opencv_coordinates(unity_pos):
    openCV_Oringin = f'OpenCVOrigin.txt'
    openCV_Oringin = np.loadtxt(openCV_Oringin).astype('float32')
    #print(openCV_Oringin)
    unity_pos = [unity_pos[0] - openCV_Oringin[0], -(unity_pos[2] - openCV_Oringin[2]),
                         unity_pos[1] - openCV_Oringin[1]]
    return unity_pos