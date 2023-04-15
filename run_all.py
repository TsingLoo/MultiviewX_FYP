import shutil
import os
import sys

import datasetParameters
import argparse
import fnmatch

parser = argparse.ArgumentParser()
parser.add_argument('-p', type=int, help='Preivew annotation count')
parser.add_argument("-c", action = "store_true",help="Clear the project files and folder on .gitignore or not.")
parser.add_argument("-k", action = "store_true",help="Keep the remains of Perception dataset or not.")
parser.add_argument("-f", action = "store_true",help="Force calibrate and generate POM, regardless of perception.")
args = parser.parse_args()
previewCount = args.p if args.p else 0


from calibrateCameraByChessboard import calibrate
from generatePOM import generate_POM
from perceptionHandler import perceptionHandler
from generateAnnotation import annotate
from vali import vali

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
    print(f"Preview annotation count: {previewCount}")
    if(previewCount < 3):
        print('''        $$$$$$$$\  $$$$$$\  $$$$$$\ $$\       $$$$$$$$\ $$$$$$$\  
        $$  _____|$$  __$$\ \_$$  _|$$ |      $$  _____|$$  __$$\ 
        $$ |      $$ /  $$ |  $$ |  $$ |      $$ |      $$ |  $$ |
        $$$$$\    $$$$$$$$ |  $$ |  $$ |      $$$$$\    $$ |  $$ |
        $$  __|   $$  __$$ |  $$ |  $$ |      $$  __|   $$ |  $$ |
        $$ |      $$ |  $$ |  $$ |  $$ |      $$ |      $$ |  $$ |
        $$ |      $$ |  $$ |$$$$$$\ $$$$$$$$\ $$$$$$$$\ $$$$$$$  |
        \__|      \__|  \__|\______|\________|\________|\_______/ ''')
        print(f"-p should be larger than 2")
        sys.exit()


    print(f"Clear the project: {args.c}")
    print(f"Keep Perception remains: {args.k}")
    print(f"Force calibrate and generate POM: {args.f}")

    print("==== Args ====")
    print()
def clear_project(path = os.getcwd()):
    # Read the .gitignore file and extract the ignored files and folders
    with open('.gitignore', 'r') as f:
        ignored_patterns = [line.strip() for line in f.readlines() if not line.startswith('#') and line.strip() != '']

    # Remove the ignored files and folders from the directory
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            file_path = os.path.join(root, name)
            if any(fnmatch.fnmatch(file_path, pattern) for pattern in ignored_patterns):
                os.remove(file_path)
        for name in dirs:
            dir_path = os.path.join(root, name)
            if any(fnmatch.fnmatch(dir_path, pattern) for pattern in ignored_patterns):
                shutil.rmtree(dir_path)


def finish():
    print()
    if(previewCount == 0):
        for file in os.listdir("."):
            if fnmatch.fnmatch(file, "bbox_cam*_frame*.png"):
                os.remove(file)

    if(args.f is not True):
        if (os.path.exists(f"rectangles.pom")):
            os.remove(f"rectangles.pom")
        if(os.path.exists(f"calibrations")):
            shutil.rmtree(f"calibrations")

    print("==== All Done ====")
    print(f"Check {os.path.join(os.getcwd(), datasetParameters.DATASET_NAME)} to get your data!")

if __name__ == '__main__':

    note()
    if(args.c):
        clear_project()
    elif(args.f):
        calibrate()
        vali()
        generate_POM()
    else:
        perceptionHandler(args.k)
        calibrate()
        vali()
        generate_POM()
        annotate(previewCount)
    finish()


