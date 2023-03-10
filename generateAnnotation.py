import os
import re
import json
import matplotlib.pyplot as plt
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


def annotate(b,s):
    DATASET_NAME = datasetParameters.DATASET_NAME
    bbox_by_pos_cam = read_pom(os.path.join(DATASET_NAME,'rectangles.pom'))
    gts = []
    for cam in range(NUM_CAM):
        gt = read_gt(cam)
        gts.append(gt)
    gts = np.concatenate(gts, axis=0)
    gts = np.unique(gts, axis=0)
    print(f'average persons per frame: {gts.shape[0] / len(np.unique(gts[:, 0]))}')
    pids_dict = {}
    os.makedirs(os.path.join(DATASET_NAME,'annotations_positions'), exist_ok=True)
    for frame in np.unique(gts[:, 0]):
        gts_frame = gts[gts[:, 0] == frame, :]
        annotations = []
        for i in range(gts_frame.shape[0]):
            pid, pos = gts_frame[i, 1:]
            if pid not in pids_dict:
                pids_dict[pid] = len(pids_dict)
            annotations.append(create_pid_annotation(pids_dict[pid], pos, bbox_by_pos_cam))
        with open(os.path.join(DATASET_NAME,'annotations_positions/{:05d}.json'.format(frame)), 'w') as fp:
            json.dump(annotations, fp, indent=4)
        if frame == 0:
            for cam in range(NUM_CAM):
                if((s is True) or (b is True)):
                    img = Image.open(os.path.join(DATASET_NAME,f'Image_subsets/C{cam + 1}/0000.png'))
                    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                    for anno in annotations:
                        anno = anno['views'][cam]
                        bbox = tuple([anno['xmin'], anno['ymin'], anno['xmax'], anno['ymax']])
                        if bbox[0] == -1 and bbox[1] == -1:
                            continue
                        cv2.rectangle(img, bbox[:2], bbox[2:], (0, 255, 0), 2)

                        cv2.putText(img, str(bbox[:2]), tuple(bbox[:2]),cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                        cv2.putText(img, str(bbox[2:]), tuple(bbox[2:]),cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                    '''cv2.circle(img, (1506,740), 5, (0, 255, 0), -1)
                    cv2.putText(img, str((1506,740)), (1626,650),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.circle(img, (1437,740), 5, (0, 255, 0), -1)
                    cv2.putText(img, str((1437,740)), (1317,650),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.circle(img, (1475,775), 5, (0, 255, 0), -1)
                    cv2.putText(img, str((1475,775)), (1355,855),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.circle(img, (1551,775), 5, (0, 255, 0), -1)
                    cv2.putText(img, str((1551,775)), (1671,855),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                    cv2.circle(img,(1567,388),5,(0,0, 255), -1)
                    cv2.putText(img, str((1567,388)), (1687,308),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.circle(img, (1490, 388), 5, (0, 0, 255), -1)
                    cv2.putText(img, str((1490, 388)), (1400, 308),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.circle(img, (1538, 396), 5, (0, 0, 255), -1)
                    cv2.putText(img, str((1538, 396)), (1500, 496),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.circle(img, (1622, 396), 5, (0, 0, 255), -1)
                    cv2.putText(img, str((1622, 396)), (1682, 496),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)'''

                    '''cv2.circle(img, (1172,897), 5, (0, 255, 0), -1)
                    cv2.putText(img, str((1172,897)), (1626,650),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.circle(img, (1206,805), 5, (0, 255, 0), -1)
                    cv2.putText(img, str((1206,805)), (1317,650),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.circle(img, (1054,772), 5, (0, 255, 0), -1)
                    cv2.putText(img, str((1054,772)), (1355,855),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.circle(img, (997,852), 5, (0, 255, 0), -1)
                    cv2.putText(img, str((997,852)), (1671,855),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                    cv2.circle(img,(1199,483),5,(0,0, 255), -1)
                    cv2.putText(img, str((1199,483)), (1687,308),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.circle(img, (1233, 450), 5, (0, 0, 255), -1)
                    cv2.putText(img, str((1233, 450)), (1400, 308),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.circle(img, (1063, 439), 5, (0, 0, 255), -1)
                    cv2.putText(img, str((1063, 439)), (1500, 496),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.circle(img, (1001, 467), 5, (0, 0, 255), -1)
                    cv2.putText(img, str((1001, 467)), (1682, 496),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)'''
                    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                    if(s is True):
                        img.save(f'bbox_cam{cam + 1}.png')
                    if(b is True):
                        plt.imshow(img)
                        plt.show()
                    pass

    pass
    print("==== Annotation Done ====")


if __name__ == '__main__':
    annotate(False,False)
