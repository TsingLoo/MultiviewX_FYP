import os
import re
import json
import shutil
import sys
import time
import datasetParameters

def printFailed(msg):
    print(msg)

def get_most_recent_perception_folder_path(perception_path):
    dataSetLists = os.listdir(perception_path)
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    valid_directories = [d for d in dataSetLists if re.match(pattern, d)]
    
    if len(valid_directories) == 0:
        printFailed("perceptionHandler.py failed. There is no valid datasets given by Unity Perception. Please use Unity Perception to generate new data.")
        sys.exit()

    valid_directories.sort(key=lambda x: os.path.getmtime(os.path.join(perception_path, x)))
    #print(valid_directories)

    path = os.path.join(perception_path, valid_directories[-1])
    print(f"Working on folder: {path}")
    return path

def prepare():
    time_stamp = time.strftime('%H%M%S',time.localtime())
    dataset_name = time_stamp + f"_C{datasetParameters.NUM_CAM}_F{datasetParameters.NUM_FRAMES}"
    if os.path.exists(dataset_name):
        print()
        print(f"It seems that PACK {dataset_name} has already been")
        print(f"Do you want to replace it with the newest data? Or it will be saved as _{dataset_name}")
        choice = ""
        while (choice != 'y' and choice != 'Y' and choice != 'n' and choice != 'N'):
            choice = input("Input:(y/n)")
            if (choice == 'y' or choice == 'Y'):
                shutil.rmtree(dataset_name)
            if (choice == 'n' or choice == 'N'):
                dataset_name = "_" + dataset_name
    os.mkdir(dataset_name,777)
    datasetParameters.DATASET_NAME = dataset_name

def perceptionHandler():
    sensorDic = {}

    perception_path = datasetParameters.PERCEPTION_PATH
    path = get_most_recent_perception_folder_path(perception_path)
    rgbLists=os.listdir(path)

    with open(os.path.join(path, os.path.join(rgbLists[0]), 'captures_000.json'), 'r') as f:
        jsonstr = f.read()
        data = json.loads(jsonstr)
        captures = data.get('captures')

        for i in range(len(captures)):
            sensor = captures[i]['sensor']
            cameraLabel = (captures[i]['filename']).split('/')[0]
            tuple = {cameraLabel: sensor['sensor_id']}
            sensorDic.update(tuple)

    for RGBdir in rgbLists[1:]:
        datasetParameters.NUM_FRAMES = len(os.listdir(os.path.join(path, RGBdir)))
        if(len(os.listdir(os.path.join(path, RGBdir))) == 0):
            print(path + " has been processed, there is no available fresh data")
            print("Do you want to delete this directory?")

            choice = ""
            while (choice != 'y' and choice != 'Y' and choice != 'n' and choice != 'N'):
                choice = input("Input:(y/n)")
                if (choice == 'y' or choice == 'Y'):
                    print(f"{path} removed")
                    shutil.rmtree(path)
                if (choice == 'n' or choice == 'N'):
                    print(path + " remains unchanged")
            printFailed("run_all.py failed, please use Unity Perception to generate new data")
            sys.exit()

    prepare()

    Image_subsets_path = os.path.join(datasetParameters.DATASET_NAME, f'Image_subsets')

    if os.path.exists(Image_subsets_path):
        print()
        print("It seems that Image_subsets has already been")
        print("Do you want to regenerate it from the latest perception dataset?")
        choice = ""
        while(choice != 'y' and choice != 'Y' and choice != 'n' and choice != 'N'):
            choice = input("Input:(y/n)")
            if(choice == 'y' or choice == 'Y'):
                shutil.rmtree(Image_subsets_path)
            if(choice == 'n' or choice == 'N'):
                print("Image_subset remains unchanged")
                return



    os.makedirs(Image_subsets_path,777)
    for key in sensorDic.keys():
        #print(key)
        os.makedirs(os.path.join(Image_subsets_path, "C" + sensorDic[key]) ,777)

    for RGBdir in rgbLists[1:]:
        #print(rgbLists)
        #print(RGBdir)
        imageIndex = 0

        RGBImages = sorted(os.listdir(os.path.join(path, RGBdir)), key=lambda x: int(re.search(r'\d+', x).group()))
        for RGBImage in RGBImages:
            string = str(imageIndex)
            destination_path = os.path.join(Image_subsets_path, "C" + sensorDic[RGBdir])
            destination_filename = f"{string.rjust(datasetParameters.RJUST_WIDTH, '0')}.{RGBImage.split('.')[1]}"
            # Copy the RGB image to the destination
            shutil.copy2(
                os.path.join(os.path.join(path, RGBdir), RGBImage),
                os.path.join(destination_path, destination_filename)
            )
            imageIndex += 1

    print(Image_subsets_path + " Generation Done")


def removeRawPerceptionFiles(keep=False):
    if not keep:
        perception_path = datasetParameters.PERCEPTION_PATH
        path = get_most_recent_perception_folder_path(perception_path)
        print(f"Delete {path}")
        shutil.rmtree(path)


if __name__ == '__main__':
    perceptionHandler()
