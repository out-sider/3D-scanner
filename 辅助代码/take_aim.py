import cv2
import numpy as np
from time import clock

size9 = 1080
size16= 1920
camera_y = np.arange(size16)
Xi = np.arange(size9)
x = int(size16 / 2)
y = int(size9 / 2)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  size16)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, size9)
kernel_dilate = np.ones((27,3), np.uint8)
radius = 10
lenth = 200
thickness = 1
brightness = 255
lower = np.array([168, 140, 180])
upper = np.array([173, 254, 254])

#print('当前分辨率为{}*{}，帧率为{}'.format(cap.get(cv2.CAP_PROP_FRAME_WIDTH ),cap.get(cv2.CAP_PROP_FRAME_HEIGHT ),cap.get(cv2.CAP_PROP_FPS )))

while(1):
    e1 = clock()
    # Take each frame
    _, frame = cap.read()
    e2 = clock()
    print('获取一帧用时%.2fms' %(1000*(e2-e1)))

    #frame = cv2.bilateralFilter(frame, 5, 50, 50)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    laser = cv2.inRange(hsv, lower, upper)  # 取颜色符合条件的区域
    mask = cv2.dilate(laser, kernel_dilate)  # 将符合条件的区域膨胀，以便做权重
    
    fit = cv2.bitwise_and(gray, gray, mask=mask)  # 只要符合颜色识别条件的灰度图
    thr = cv2.equalizeHist(fit)

    e3 = clock()
    print('图像处理用时%.2fms' % (1000 * (e3 - e2)))

    result = np.zeros((size9, size16), np.uint8)
    for z in camera_y:
        if thr[:, z].sum() != 0:  # 跳过整条都是黑的情况
            si = np.array(Xi * thr[:, z], np.uint32)
            X0 = si.sum() / thr[:, z].sum()  # 计算加权平均的点的轴坐标
            px = X0 - size9 / 2  # 计算偏移像素
        else:
            continue
        result[int(X0),z] = 255
    # 理论上更快的数组操作
    e4 = clock()
    print('获取重心用时%.2fms' % (1000 * (e4 - e3)))

    frame = cv2.line(frame, (0, y),(size16, y), brightness, thickness)
    result = cv2.line(result, (0, y),(size16, y), brightness, thickness)

    cv2.imshow('frame',frame)
    cv2.imshow('gray', gray)
    cv2.imshow('threshold', thr)
    cv2.imshow('result', result)

    e5 = clock()
    print('总帧率%.2f\n' % (1/ (e5 - e1)))

    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()