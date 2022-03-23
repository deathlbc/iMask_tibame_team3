
程式目標:

-----------------------------------------------------------------------------------------------

使用訓練好的YOLOv5s模型，偵測到 without_mask 和 incorrect_mask之後，呼叫蜂鳴器發出警示。

另外，以Thread進行平行處理，解決畫面會因為發出警告而卡頓問題。


模型下載:

-----------------------------------------------------------------------------------------------

YOLOv5s model: #下載 best.engine

https://drive.google.com/drive/u/0/folders/1eV2ZZQv4wJKygbK7i38Wwnz2EwPSmKDz

data.yaml: #下載 data.yaml

https://drive.google.com/file/d/1lWSgkz4kvbbnZYaoqTtPG52PGUdTMiYE/view?usp=sharing


使用方法:

-----------------------------------------------------------------------------------------------

# 切換到 yolov5目錄底下

cd yolov5

# 下載

python3 thread_test.py --weights ../best.engine --imgsz 320 320 --source 0 --data ../data.yaml

