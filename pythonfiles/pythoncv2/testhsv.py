import cv2
import numpy as np
cap = cv2.VideoCapture(0)

def do_nothing(val):
    pass
cv2.namedWindow("TrackBar")

cv2.createTrackbar("Hue_Low","TrackBar",100,179,do_nothing)
cv2.createTrackbar("Hue_High","TrackBar",100,179,do_nothing)
cv2.createTrackbar("Sat_Low","TrackBar",100,255,do_nothing)
cv2.createTrackbar("Sat_High","TrackBar",100,255,do_nothing)
cv2.createTrackbar("Val_Low","TrackBar",100,255,do_nothing)
cv2.createTrackbar("Val_High","TrackBar",100,255,do_nothing)


while True:
    _, frame = cap.read()
    frame = cv2.flip(frame,1)
    frame_hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    hue_low = cv2.getTrackbarPos("Hue_Low","TrackBar")
    hue_high = cv2.getTrackbarPos("Hue_High","TrackBar")
    sat_low = cv2.getTrackbarPos("Sat_Low","TrackBar")
    sat_high = cv2.getTrackbarPos("Sat_High","TrackBar")
    val_low = cv2.getTrackbarPos("Val_Low","TrackBar")
    val_high = cv2.getTrackbarPos("Val_High","TrackBar")

    mask = cv2.inRange(frame_hsv,(hue_low,sat_low,val_low),(hue_high,sat_high,val_high))
    result = cv2.bitwise_and(frame,frame,mask=mask)
    cv2.imshow("Frame",frame)
    cv2.imshow("Frame_mask",mask)
    cv2.imshow("Result",result)
    key = cv2.waitKey(5) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        hsv = np.array([[hue_low,sat_low,val_low],[hue_high,sat_high,val_high]])
        np.save("hsv\hsv_value.npy",hsv)

cv2.destroyAllWindows()
cap.release()
print(np.load("hsv\hsv_value.npy"))