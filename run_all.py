import shutil
import os
import datasetParameters
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-a", action = "store_true",help="Annotate and show the bbox on the first frame of each camera or not.")
parser.add_argument("-c", action = "store_true",help="Clear the project files and folder on .gitignore or not.")
parser.add_argument("-s", action = "store_true",help="Save the bbox on the first frame of each camera or not.")
parser.add_argument("-k", action = "store_true",help="Keep the remains of Perception dataset or not.")
parser.add_argument("-f", action = "store_true",help="Force calibrate and generate POM, regardless of perception.")
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
    print(f"Clear the project: {args.c}")
    print(f"Save bbox: {args.s}")
    print(f"Keep Perception remains: {args.k}")
    print(f"Force calibrate and generate POM: {args.f}")

    print("==== Args ====")
    print()
def clear_project(folder_path = os.getcwd()):
    unwanted_files_and_folders = []

    # Read the .gitignore file, if it exists
    gitignore_path = os.path.join(folder_path, ".gitignore")
    if os.path.isfile(gitignore_path):
        with open(gitignore_path, "r") as f:
            for line in f.readlines():
                # Remove newline characters and ignore comments
                line = line.strip()
                if not line.startswith("#"):
                    # Ignore empty lines and directories (ends with '/')
                    if line != "" and not line.endswith("/"):
                        unwanted_files_and_folders.append(line)

    # Delete all files and folders in the folder that are in the allowed list
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if file_name in unwanted_files_and_folders:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)


def finish():
    print()
    if(args.s is not True):
        for i in range(datasetParameters.NUM_CAM):
            if(os.path.exists(f"bbox_cam{i+1}.png")):
                os.remove(f"bbox_cam{i+1}.png")

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
        generate_POM()
    else:
        perceptionHandler(args.k)
        calibrate()
        generate_POM()
        annotate(args.a,args.s)
    finish()


