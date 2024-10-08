import cv2
import os

file = 'images\image1.jpg'
img = cv2.imread(file)
imgGray = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
pnumber = 0
def do_nothing(value):
    pass

cv2.namedWindow("TrackBar")
cv2.createTrackbar("Threshold", "TrackBar", 0, 255, do_nothing)
cv2.createTrackbar("cannyLow", "TrackBar",0,255,do_nothing)
cv2.createTrackbar("cannyHigh", "TrackBar",0,255,do_nothing)

while True:
    threshNum = cv2.getTrackbarPos("Threshold", "TrackBar")
    low = cv2.getTrackbarPos("cannyLow", "TrackBar")
    high = cv2.getTrackbarPos("cannyHigh", "TrackBar")
    _, imgThresh = cv2.threshold(imgGray,threshNum,255, cv2.THRESH_BINARY)
    imgCanny = cv2.Canny(imgGray,low,high)
    cv2.imshow("TeddyBear",imgGray)
    cv2.imshow("Threshold", imgThresh)
    cv2.imshow("Cannybear",imgCanny)
    key = cv2.waitKey(5) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        save_file = f'images/capturedimage{pnumber}.jpg'
        cv2.imwrite(save_file,imgCanny)
        pnumber +=1

cv2.destroyAllWindows()
os.system("cls")