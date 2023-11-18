More information：[Notes of MultiviewX_Perception](http://www.tsingloo.com/2023/03/01/0a2bf39019914a06954a4506b9f0ca37/) 

# Args

MultiviewX_Perception可以接受命令行参数，从而用户可以快速高效地产生数据集。当未接收到相关参数时候，不会启用相关功能。

`-a` ：Annotate and show the bbox on the first frame of each camera or not.

`-s` ：Save the bbox on the first frame of each camera or not.

`-k` ：Keep the remains of Perception dataset or not.

`-f` ：Force calibrate and generate POM, regardless of perception.

`-p n`: Provide preview for the front n frames. ex. `-p 5` will provide 5 frames to preview 

`-v` ：Generate Overlap view for the dataset

`-view path` ：Generate Overlap view for the specified dataset, there should be folder `calibrations` in the given path. ex. `-view D:\Wildtrack`

![Camera 6](http://images.tsingloo.com/image-20231118223027230.png)

![左图为本工具对 Wildtrack 的结果，右图(有一定变形)为参考](http://images.tsingloo.com/image-20231118221443880.png)

![cam1_frames](http://images.tsingloo.com/cam1_frames.gif)
