import shutil
import time
import os

import datasetParameters

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-a", action = "store_true",help="Annotate and show the bbox on the first frame of each camera or not.")
parser.add_argument("-s", action = "store_true",help="Save the bbox on the first frame of each camera or not.")
parser.add_argument("-k", action = "store_true",help="Keep the remains of Perception dataset or not.")

args = parser.parse_args()

from calibrateCameraByChessboard import calibrate
from generatePOM import generate_POM
from perceptionHandler import perceptionHandler
from generateAnnotation import annotate

def note():
    print('''                             ,,          ,,              ,,                                                                           
`7MMM.     ,MMF'           `7MM   mm     db              db                        `YMM'   `MP'     `7MM"""YMM `YMM'   `MM'`7MM"""Mq. 
  MMMb    dPMM               MM   MM                                                 VMb.  ,P         MM    `7   VMA   ,V    MM   `MM.
  M YM   ,M MM `7MM  `7MM    MM mmMMmm `7MM `7M'   `MF'`7MM  .gP"Ya `7M'    ,A    `MF'`MM.M'          MM   d      VMA ,V     MM   ,M9 
  M  Mb  M' MM   MM    MM    MM   MM     MM   VA   ,V    MM ,M'   Yb  VA   ,VAA   ,V    MMb           MM""MM       VMMP      MMmmdM9  
  M  YM.P'  MM   MM    MM    MM   MM     MM    VA ,V     MM 8M""""""   VA ,V  VA ,V   ,M'`Mb.         MM   Y        MM       MM       
  M  `YM'   MM   MM    MM    MM   MM     MM     VVV      MM YM.    ,    VVV    VVV   ,P   `MM.        MM            MM       MM       
.JML. `'  .JMML. `Mbod"YML..JMML. `Mbmo.JMML.    W     .JMML.`Mbmmd'     W      W  .MM:.  .:MMa.    .JMML.        .JMML.   .JMML.    ''')
    print()
    print("""To utilize this project, you could refer to :
    1. Notes of CalibrateTool: http://www.tsingloo.com/2023/03/01/0a2bf39019914a06954a4506b9f0ca37/ 
    2. Unity Perception Package: https://docs.unity3d.com/Packages/com.unity.perception@1.0/manual/index.html""")
    print()
    print("==== NOTE ====")
    print()
    print(f"Annotate and show bbox: {args.a}")
    print(f"Save bbox: {args.s}")
    print(f"Keep Perception remains: {args.k}")
    print("==== Args ====")
    print()
def finish():
    print()
    if(args.s is not True):
        for i in range(datasetParameters.NUM_CAM):
            if(os.path.exists(f"bbox_cam{i+1}.png")):
                os.remove(f"bbox_cam{i+1}.png")

    print(f"Check {datasetParameters.DATASET_NAME} to get your data!")

if __name__ == '__main__':


    note()
    perceptionHandler(args.k)

    calibrate()
    generate_POM()
    annotate(args.a,args.s)

    finish()


