import cv2

cap = cv2.VideoCapture(0)

inumber = 0

while True:
    _, frame = cap.read()
    frame_flp = cv2.flip(frame,1)
    cv2.imshow("flipCamera",frame_flp)

    key = cv2.waitKey(5) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        save_file = f'images/capture{inumber}.jpg'
        cv2.imwrite(save_file,frame_flp)
        inumber +=1
                
cap.release()
cv2.destroyAllWindows()