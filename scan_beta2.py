import cv2
import numpy as np
import serial
from time import clock,sleep,strftime
import math
#import mcubes as mc

start = clock()


#硬件参数
l = 45#单位毫米,摄像头到激光线垂线长
h = 103.5#单位毫米，摄像头沿激光方向与旋转中心的距离
f = 981#单位像素，摄像头焦距
beta = math.atan(h/l)#单位弧度，摄像头中心线与到垂线夹角
angle_one_time = 1.8 #步进电机步进角
size9 = 720
size16= 1280
offset_x= size9/2
#硬件参数end

#减少计算开销
camera_y = np.arange(size16)
Xi = np.arange(size9)
axis_z = 101.5*(camera_y - size16/2)/f + 0
kernel_d = np.ones((27, 5), np.uint8)
kernel_e = np.ones((10, 5), np.uint8)
lower = np.array([168, 140, 180])
upper = np.array([173, 254, 254])

#初始化
se = serial.Serial('com9',115200,timeout=0.002,stopbits=serial.STOPBITS_ONE)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  size16)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, size9)
cap.read()
#初始化end

def move():
    se.write("m".encode('utf-8'))
    #sleep(0.01)
    #get = se.readline().decode('utf-8')[:-2]
    #print('第{0}次收到{1}'.format(mov,get))

def write2file(pc,filename):
    np.savetxt(filename,pc, fmt='%.2f',newline='\n', header='')
    # 'VERSION .7\n\
    # FIELDS x y z\n\
    # SIZE 4 4 4\n\
    # TYPE F F F\n\
    # COUNT 1 1 1\n\
    # WIDTH {0}\n\
    # HEIGHT 1\n\
    # VIEWPOINT 0 0 0 1 0 0 0\n\
    # POINTS {0}\n\
    # DATA ascii'

def get_position(cap,angle):
    _, frame = cap.read()
    e2 = clock()
    print('获取一帧用时%.2fms' % (1000 * (e2 - e1)))

    frame = cv2.bilateralFilter(frame, 5, 50, 50)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    laser = cv2.inRange(hsv, lower, upper)  # 取颜色符合条件的区域
    mask = cv2.dilate(laser, kernel_d)  # 将符合条件的区域膨胀，以便做权重
    mask = cv2.erode(mask,kernel_e)
    fit = cv2.bitwise_and(gray, gray, mask=mask)  # 只要符合颜色识别条件的灰度图
    thr = cv2.equalizeHist(fit)
    e3 = clock()
    print('图像处理用时%.2fms' % (1000 * (e3 - e2)))

    poi = np.array([0,0,0])
    for z in camera_y:
        if thr[:,z].sum() != 0:  # 跳过整条都是黑的情况
            #print(Xi.shape)
            #print(thr.shape)
            si = np.array(Xi * thr[:,z], np.uint32)  # si是加权值，Xi*gray[Xi]，用32位是因为255×1920需要19位
            X0 = si.sum() / thr[:,z].sum()  # 计算加权平均的点的轴坐标
            px = X0 - offset_x    #计算偏移像素,负值在左
            r = l*math.tan(beta) - l*math.tan(beta+math.atan(px/f))  #r[y]是第y高度离柱坐标中心的距离
            if r>1000:
                continue
            #print('距离%.2fmm'%r)
            poi_new = np.array([r*math.cos(angle/180*math.pi),r*math.sin(angle/180*math.pi),axis_z[z]])
            #print('poi_new是：',poi_new)
            poi = np.vstack((poi,poi_new))
            #print(poi)
        else:
            continue
    e4 = clock()
    print('获取重心用时%.2fms' % (1000 * (e4 - e3)))
    return poi

points = np.array([0,0,0])
tem = cap.read()
tem = cap.read()
for mov in range(int(360/angle_one_time)):
    e1 = clock()
    points = np.vstack((points, get_position(cap, mov*angle_one_time)))
    move()
    ee = clock()
    fps = 1 / (ee - e1)
    print('第%d次帧率约%.2ffps\n' %(mov,fps))
se.write("s".encode('utf-8'))#用完关步进电机
write2file(points,"D:\\temps\\dianyun_{}@{}_{}@h={}_l={}.xyz".format(strftime('%m-%d %H-%M'),size9,size16,h,l))

e5 = clock()
print('写入文件用时%.2fms' % (1000 * (e5 - ee)))
print('总用时%.2fs' %(e5-start))
