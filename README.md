# Toolkits for MultiviewX dataset

```
@inproceedings{hou2020multiview,
  title={Multiview Detection with Feature Perspective Transformation},
  author={Hou, Yunzhong and Zheng, Liang and Gould, Stephen},
  booktitle={ECCV},
  year={2020}
}
```

# CalibrateTool 

[Notes of CalibrateTool](http://www.tsingloo.com/2023/03/01/0a2bf39019914a06954a4506b9f0ca37/)

CalibrateTool是一个在Unity3D中为一个或多个相机，产生多个虚拟的不同角度朝向的棋盘格数据且给出待标定相机对应内外参的工具。其生成的虚拟棋盘数据等效于利用OpenCV中`cv.findChessboardCorners`所产生的结果。

同时，CalibrateTool 可以完成一些运行 [MultiviewX_FYP](https://github.com/TsingLoo/MultiviewX_FYP) 所需要的设置，诸如设置地图大小、地图格点起始位置等。

## Overview

The MultiviewX dataset dedicates to multiview synthetic pedestrian detection. Using pedestrian models from [PersonX](https://github.com/sxzrt/Dissecting-Person-Re-ID-from-the-Viewpoint-of-Viewpoint), in Unity, we build a novel synthetic dataset MultiviewX. It follows the [WILDTRACK dataset](https://www.epfl.ch/labs/cvlab/data/data-wildtrack/) for set-up, annotation, and structure. 

![alt text](https://hou-yz.github.io/images/eccv2020_mvdet_multiviewx_dataset.jpg "Visualization of MultiviewX dataset")

The MultiviewX dataset is generated on a 25 meter by 16 meter playground. It has 6 cameras that has overlapping field-of-view. The images in MultiviewX dataset are of high resolution, 1920x1080, and are synchronized. To fully exploit the complementary views, calibrations are also provided in MultiviewX dataset. 

![alt text](https://hou-yz.github.io/images/eccv2020_mvdet_multiviewx_demo.gif "Detection results on MultiviewX dataset using MVDet")


## Downloads
Please refer to this [link](https://1drv.ms/u/s!AtzsQybTubHfgP9BJt2g7R_Ku4X3Pg?e=GFGeVn) for download.

## Toolkits for MultiviewX dataset.

This repo includes the toolkits and utilities for bulding MultiviewX dataset.

How to's
- download (from [link](https://anu365-my.sharepoint.com/:u:/g/personal/u6852178_anu_edu_au/EZ9hISq6FxBItIsdIDkapmUBGIK7Fn9LVIAuUT8NltKDBw?e=atMYbI)) and copy the 2d/3d bbox annotations into `/matchings`.
- run the following command.
```shell script
python run_all.py
```
- done.

## Evaluation

For multiview pedestiran detection, MultiviewX follows the same evaluation scheme as Wildtrack with MODA, MODP, precission, and recall. Evaluation toolkit can be found [here](https://github.com/hou-yz/MVDet/tree/master/multiview_detector/evaluation). 

## Leaderboards


| Method            | MODA | MODP | Precision | Recall |
|-------------------|:----:|:----:|:---------:|:------:|
| RCNN & clustering [[cite]](https://openaccess.thecvf.com/content_cvpr_2016/html/Xu_Multi-View_People_Tracking_CVPR_2016_paper.html) | 18.7 | 46.4 |    63.5   |  43.9  |
| DeepMCD          [[cite]](https://ieeexplore.ieee.org/abstract/document/8260742/) | 70.0 | 73.0 |    95.7   |  73.3  |
| Deep-Occlusion   [[cite]](https://openaccess.thecvf.com/content_iccv_2017/html/Baque_Deep_Occlusion_Reasoning_ICCV_2017_paper.html) | 76.8 | 59.7 |    97.8   |  70.2  |
| MVDet    [[cite]](https://arxiv.org/abs/2007.07247) [[code]](https://github.com/hou-yz/MVDet) | 83.9 | 79.6 |    96.8   |  86.7  |
