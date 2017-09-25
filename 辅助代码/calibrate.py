import numpy as np
import cv2
import glob
import matplotlib.pyplot as plt

cap = cv2.VideoCapture(0)
plt.ion()
# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((7*7,3))
objp[:,:2] = 17.564*np.mgrid[0:7,0:7].T.reshape(-1,2)
objp = objp.astype('float32')


# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

i=0
fx = np.zeros(40)
fy = np.zeros(40)
while(1):
    _,img = cap.read()
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (7,7),None)

    k = cv2.waitKey(5) & 0xFF
    # If found, add object points, image points (after refining them)
    if ret == True and k==99:
        i += 1
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)
        # Draw and display the corners
        img = cv2.drawChessboardCorners(img, (7,7), corners2,ret)
        _, mtx, dist, _, _ = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
        h, w = img.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
        dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
        fx[i] = mtx[0,0]
        fy[i] = mtx[1,1]
        print('第%d次fx=%.2f,fy=%.2f'%(i,mtx[0,0],mtx[1,1]))

        #plt.plot(i,mtx[1,1])

        cv2.imshow('AFTER',dst)
        plt.show()
    cv2.imshow('BEFORE',img)
    if k == 27:
        break
print('变换矩阵为\n',mtx)
print('dist=\n',dist)

cv2.destroyAllWindows()