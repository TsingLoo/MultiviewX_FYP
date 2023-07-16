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
parser.add_argument("-s", action = "store_true",help="Disable multithread optimization when the number of cameras is less than 7")
args = parser.parse_args()
previewCount = args.p if args.p else 0


from calibrateCameraByChessboard import calibrate
from generatePOM import generate_POM
from perceptionHandler import perceptionHandler
from perceptionHandler import removeRawPerceptionFiles
from generateAnnotation import annotate
from vali import vali
from generateView import generate_View
from generateView import draw_views

def note():
    print('''    $$\      $$\           $$\   $$\     $$\            $$\                         $$\   $$\         $$$$$$$\                                                      $$\     $$\                     
    $$$\    $$$ |          $$ |  $$ |    \__|           \__|                        $$ |  $$ |        $$  __$$\                                                     $$ |    \__|                    
    $$$$\  $$$$ |$$\   $$\ $$ |$$$$$$\   $$\ $$\    $$\ $$\  $$$$$$\  $$\  $$\  $$\ \$$\ $$  |        $$ |  $$ | $$$$$$\   $$$$$$\   $$$$$$$\  $$$$$$\   $$$$$$\  $$$$$$\   $$\  $$$$$$\  $$$$$$$\  
    $$\$$\$$ $$ |$$ |  $$ |$$ |\_$$  _|  $$ |\$$\  $$  |$$ |$$  __$$\ $$ | $$ | $$ | \$$$$  /         $$$$$$$  |$$  __$$\ $$  __$$\ $$  _____|$$  __$$\ $$  __$$\ \_$$  _|  $$ |$$  __$$\ $$  __$$\ 
    $$ \$$$  $$ |$$ |  $$ |$$ |  $$ |    $$ | \$$\$$  / $$ |$$$$$$$$ |$$ | $$ | $$ | $$  $$<          $$  ____/ $$$$$$$$ |$$ |  \__|$$ /      $$$$$$$$ |$$ /  $$ |  $$ |    $$ |$$ /  $$ |$$ |  $$ |
    $$ |\$  /$$ |$$ |  $$ |$$ |  $$ |$$\ $$ |  \$$$  /  $$ |$$   ____|$$ | $$ | $$ |$$  /\$$\         $$ |      $$   ____|$$ |      $$ |      $$   ____|$$ |  $$ |  $$ |$$\ $$ |$$ |  $$ |$$ |  $$ |
    $$ | \_/ $$ |\$$$$$$  |$$ |  \$$$$  |$$ |   \$  /   $$ |\$$$$$$$\ \$$$$$\$$$$  |$$ /  $$ |        $$ |      \$$$$$$$\ $$ |      \$$$$$$$\ \$$$$$$$\ $$$$$$$  |  \$$$$  |$$ |\$$$$$$  |$$ |  $$ |
    \__|     \__| \______/ \__|   \____/ \__|    \_/    \__| \_______| \_____\____/ \__|  \__|$$$$$$\ \__|       \_______|\__|       \_______| \_______|$$  ____/    \____/ \__| \______/ \__|  \__|
                                                                                              \______|                                                  $$ |                                        
                                                                                                                                                        $$ | ''')
    print()
    print("""To utilize this project, you could refer to :
    1. Notes of CalibrateTool: http://www.tsingloo.com/2023/03/01/0a2bf39019914a06954a4506b9f0ca37/ 
    2. Unity Perception Package: https://docs.unity3d.com/Packages/com.unity.perception@1.0/manual/index.html""")
    print()
    print("==== NOTE ====")
    print()
    print(f"Preview annotation count: {previewCount}")
    if(previewCount < 3 and previewCount != 0):
        print('''''')
        print(f"-p should be larger than 2")
        sys.exit()


    print(f"Clear the project: {args.c}")
    print(f"Keep Perception remains: {args.k}")
    print(f"Force calibrate and generate POM: {args.f}")
    print(f"Disable multithread optimization: {args.s}")


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

    removeRawPerceptionFiles(args.k)

    print("==== All Done ====")
    print(f"Check {os.path.join(os.getcwd(), datasetParameters.DATASET_NAME)} to get your data!")

if __name__ == '__main__':

    threadCount = 36
    #generate_View()

    note()
    if(args.c):
        clear_project()
    elif(args.f):
        calibrate(threadCount ,args.s)
        #vali()
        generate_POM()
    else:
        perceptionHandler()
        calibrate(threadCount , args.s)
        #vali()
        generate_View()
        draw_views()
        generate_POM()
        annotate(previewCount,threadCount,args.s)
    finish()


