import os
import json
import shutil
import sys
import time
import datasetParameters

def printFailed(msg):
    print('''$$$$$$$$\  $$$$$$\  $$$$$$\ $$\       $$$$$$$$\ $$$$$$$\  
    $$  _____|$$  __$$\ \_$$  _|$$ |      $$  _____|$$  __$$\ 
    $$ |      $$ /  $$ |  $$ |  $$ |      $$ |      $$ |  $$ |
    $$$$$\    $$$$$$$$ |  $$ |  $$ |      $$$$$\    $$ |  $$ |
    $$  __|   $$  __$$ |  $$ |  $$ |      $$  __|   $$ |  $$ |
    $$ |      $$ |  $$ |  $$ |  $$ |      $$ |      $$ |  $$ |
    $$ |      $$ |  $$ |$$$$$$\ $$$$$$$$\ $$$$$$$$\ $$$$$$$  |
    \__|      \__|  \__|\______|\________|\________|\_______/ ''')
    print(msg)

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

def movefile(srcfile,dstpath):                       # 移动函数
    if not os.path.isfile(srcfile):
        print ("%s not exist!"%(srcfile))
    else:
        fpath,fname=os.path.split(srcfile)             # 分离文件名和路径
        if not os.path.exists(dstpath):
            os.makedirs(dstpath)                       # 创建路径
        print (os.path.join(dstpath , fname))
        shutil.move(srcfile, os.path.join(dstpath , fname))          # 移动文件
        print ("move %s -> %s"%(srcfile, os.path.join(dstpath , fname)))

def perceptionHandler(keep):
    sensorDic = {}

    perception_path = datasetParameters.PERCEPTION_PATH
    dataSetLists=os.listdir(perception_path)
    if(len(dataSetLists) == 0 ):
        printFailed("perceptionHandler.py failed, there is no valid datasets given by Unity Perception, please use Unity Perception to generate new data")
        sys.exit()
    dataSetLists.sort(key=lambda x:os.path.getmtime((perception_path +"\\"+x)))

    path = os.path.join(perception_path, dataSetLists[-1])
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
            print( path + " has been processed, there is no available fresh data")
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
        os.makedirs(os.path.join(Image_subsets_path, "C" + sensorDic[key]) ,777)

    for RGBdir in rgbLists[1:]:
        imageIndex = 0

        for RGBImage in os.listdir(os.path.join(path, RGBdir)):
            #print(RGBImage)
            string = str(imageIndex)
            shutil.move(os.path.join(os.path.join(path, RGBdir),RGBImage),
                      os.path.join(os.path.join(Image_subsets_path, "C" + sensorDic[RGBdir]), string.rjust(datasetParameters.RJUST_WIDTH, '0') + "." + RGBImage.split(".")[1]))
            imageIndex = imageIndex + 1

    if(not keep):
        print(f"Delete {path}")
        shutil.rmtree(path)

    print(Image_subsets_path + " Generation Done")

if __name__ == '__main__':
    perceptionHandler(False)
