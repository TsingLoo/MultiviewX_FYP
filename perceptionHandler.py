import os
import json
import shutil
from glob import glob
import datasetParameters


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

def perceptionHandler():
    sensorDic = {}

    perception_path = f'perception'
    dataSetLists=os.listdir(perception_path)
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
        if(len(os.listdir(os.path.join(path, RGBdir))) == 0):
            print( path + " has been processed")
            print("Do you want to delete this directory?")
            choice = ""
            while (choice != 'y' and choice != 'Y' and choice != 'n' and choice != 'N'):
                choice = input("Input:(y/n)")
                if (choice == 'y' or choice == 'Y'):
                    shutil.rmtree(path)
                if (choice == 'n' or choice == 'N'):
                    print(path + " remains unchanged")
                    return
            return

    Image_subsets_path = f'Image_subsets'

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
            os.rename(os.path.join(os.path.join(path, RGBdir),RGBImage),
                      os.path.join(os.path.join(Image_subsets_path, "C" + sensorDic[RGBdir]), string.rjust(datasetParameters.RJUST_WIDTH, '0') + "." + RGBImage.split(".")[1]))
            imageIndex = imageIndex + 1


    print(Image_subsets_path + " Generation Done")

if __name__ == '__main__':
    perceptionHandler()
