import os
import re
import json
import cv2
from PIL import Image

import datasetParameters
from unitConversion import *


def read_pom(fpath):
    bbox_by_pos_cam = {}
    cam_pos_pattern = re.compile(r'(\d+) (\d+)')
    cam_pos_bbox_pattern = re.compile(r'(\d+) (\d+) ([-\d]+) ([-\d]+) (\d+) (\d+)')
    with open(fpath, 'r') as fp:
        for line in fp:
            if 'RECTANGLE' in line:
                cam, pos = map(int, cam_pos_pattern.search(line).groups())
                if pos not in bbox_by_pos_cam:
                    bbox_by_pos_cam[pos] = {}
                if 'notvisible' in line:
                    bbox_by_pos_cam[pos][cam] = [-1, -1, -1, -1]
                else:
                    cam, pos, left, top, right, bottom = map(int, cam_pos_bbox_pattern.search(line).groups())
                    bbox_by_pos_cam[pos][cam] = [left, top, right, bottom]
    return bbox_by_pos_cam


def read_gt(cam):

    # 最后一个坐标是脚底的位置
    # 坐标数组 ... [1723.596   471.1655] [1421.27    544.6304]
    #visualize_foot_image = points_2d[points_2d[:, 0] == 0, -2:]

    gt_3d = np.loadtxt(f'matchings/Camera{cam + 1}_3d.txt')
    #print(gt_3d)
    #删去脚底点不在Grid内的人
    gt_3d = gt_3d[np.where(np.logical_and(gt_3d[:, -3] >= 0, gt_3d[:, -3] <= MAP_WIDTH))[0], :]
    gt_3d = gt_3d[np.where(np.logical_and(gt_3d[:, -2] >= 0, gt_3d[:, -2] <= MAP_HEIGHT))[0], :]

    frame, pid = gt_3d[:, 0], gt_3d[:, 1]

    foot_3d_coord = gt_3d[:, -3:-1].transpose()
    #print(foot_3d_coord)
    pos = get_pos_from_worldcoord(foot_3d_coord)
    return np.stack([frame, pid, pos], axis=1).astype(int)


def create_pid_annotation(pid, pos, bbox_by_pos_cam):
    person_annotation = {'personID': int(pid), 'positionID': int(pos), 'views': []}
    for cam in range(len(bbox_by_pos_cam[pos])):
        bbox = bbox_by_pos_cam[pos][cam]
        view_annotation = {'viewNum': cam, 'xmin': int(bbox[0]), 'ymin': int(bbox[1]),
                           'xmax': int(bbox[2]), 'ymax': int(bbox[3])}
        person_annotation['views'].append(view_annotation)
    return person_annotation


def annotate(previewCount):
    lastFrameIndex = previewCount - 1
    DATASET_NAME = datasetParameters.DATASET_NAME
    bbox_by_pos_cam = read_pom(os.path.join(DATASET_NAME, 'rectangles.pom'))
    gts = []
    for cam in range(NUM_CAM):
        gt = read_gt(cam)
        gts.append(gt)
    gts = np.concatenate(gts, axis=0)
    gts = np.unique(gts, axis=0)
    print(f'average persons per frame: {gts.shape[0] / len(np.unique(gts[:, 0]))}')
    pids_dict = {}
    os.makedirs(os.path.join(DATASET_NAME, 'annotations_positions'), exist_ok=True)
    for frame in np.unique(gts[:, 0]):
        gts_frame = gts[gts[:, 0] == frame, :]
        annotations = []
        for i in range(gts_frame.shape[0]):
            pid, pos = gts_frame[i, 1:]
            if pid not in pids_dict:
                pids_dict[pid] = len(pids_dict)
            annotations.append(create_pid_annotation(pids_dict[pid], pos, bbox_by_pos_cam))

        with open(os.path.join(DATASET_NAME, 'annotations_positions/{:05d}.json'.format(frame)), 'w') as fp:
            json.dump(annotations, fp, indent=4)

        if lastFrameIndex != 0 and frame <= lastFrameIndex:
            for cam in range(NUM_CAM):
                annotationPath = os.path.join(DATASET_NAME, 'Image_subsets', f'C{cam + 1}')
                imageLists = os.listdir(annotationPath)
                for image in imageLists:
                    img_file_name = os.path.splitext(image)[0]
                    img_frame_index = int(img_file_name.split('_')[-1])
                    if img_frame_index == frame:
                        img = Image.open(os.path.join(os.path.join(annotationPath, image)))
                        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

                        for anno in annotations:
                            pid = anno['personID']
                            anno = anno['views'][cam]
                            bbox = tuple([anno['xmin'], anno['ymin'], anno['xmax'], anno['ymax']])
                            if bbox[0] == -1 and bbox[1] == -1:
                                continue
                            cv2.rectangle(img, bbox[:2], bbox[2:], (0, 255, 0), 2)
                            cv2.putText(img, str(pid), ((bbox[:2][0]+bbox[2:][0])//2, (bbox[:2][1]+bbox[2:][1])//2), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                        (0, 255, 255), 2)

                            cv2.putText(img, str(bbox[:2]), tuple(bbox[:2]), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                        (255, 255, 255), 2)
                            cv2.putText(img, str(bbox[2:]), tuple(bbox[2:]), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                        (255, 255, 255), 2)
                        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                        img.save(f'bbox_cam{cam + 1}_frame{frame}.png')

    if(not previewCount == 0):
        for cam in range(NUM_CAM):
            gif = []
            for frame in range(previewCount):
                filename = f"bbox_cam{cam + 1}_frame{frame}.png"
                img = Image.open(filename)
                gif.append(img)

            gif[0].save(f"cam{cam + 1}_frames.gif", format="GIF", append_images=gif[1:], save_all=True, duration=100,
                    loop=0)

            #gif[0].show()

if __name__ == '__main__':
    annotate(0)
