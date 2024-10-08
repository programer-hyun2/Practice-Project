import cv2
import os
import numpy as np

file = 'images\image2.png'
img = cv2.imread(file)
imgGray = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
def do_nothing(value):
    pass
threBGR_low = np.zeros(3)
threBGR_high = np.zeros(3)

cv2.namedWindow("TrackBar")
cv2.createTrackbar("Red_low", "TrackBar", 0, 255, do_nothing)
cv2.createTrackbar("Red_high", "TrackBar", 255, 255, do_nothing)
cv2.createTrackbar("Green_low", "TrackBar", 0, 255, do_nothing)
cv2.createTrackbar("Green_high", "TrackBar", 255, 255, do_nothing)
cv2.createTrackbar("Blue_low", "TrackBar", 0, 255, do_nothing)
cv2.createTrackbar("Blue_high", "TrackBar", 255, 255, do_nothing)

while True:
    
    threBGR_low[0] = cv2.getTrackbarPos("Blue_low","TrackBar")
    threBGR_high[0] = cv2.getTrackbarPos("Blue_high","TrackBar")
    
    threBGR_low[1] = cv2.getTrackbarPos("Green_low","TrackBar")
    threBGR_high[1] = cv2.getTrackbarPos("Green_high","TrackBar")

    threBGR_low[2] = cv2.getTrackbarPos("Red_low","TrackBar")
    threBGR_high[2] = cv2.getTrackbarPos("Red_high","TrackBar")
    
    imgMask = cv2.inRange(img,threBGR_low,threBGR_high)
    
    contour,_ = cv2.findContours(imgMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    imgCont = cv2.drawContours(img, contour, -1, 50, 3)

    cv2.imshow("apples", img)
    cv2.imshow("applesmask", imgMask)
    cv2.imshow("applescontour", imgCont)
    
    key = cv2.waitKey(5) & 0xFF
    if key == ord('q'):
        break

cv2.destroyAllWindows()
os.system("cls")