import cv2

haar_path = "xml\haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(haar_path)
smile_path = "xml\haarcascade_smile.xml"
smile_casecade = cv2.CascadeClassifier(smile_path)
cap = cv2.VideoCapture(0)
inumber = 0
while True:
    _, frame = cap.read()
    frame = cv2.flip(frame,1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5, minSize=(30,30))
    for (x,y,w,h) in faces:
        #cv2.rectangle(frame, (x,y+round(h*0.35)), (x+w, y+round(h*0.45)), (0,0,0), -1)
        smile_roi= gray[y:y+h, x:x+w]
        smiles = smile_casecade.detectMultiScale(smile_roi, 1.8, 20, minSize=(30,30))
        for (sx,sy,sw,sh) in smiles:
            cv2.rectangle(frame, (x+sx, y+sy), (x+sx+sw, y+sy+sh), (255,255,255), 2)

    cv2.imshow("frame", frame)
    key = cv2.waitKey(5) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        save_file = f'images/capture{inumber}.jpg'
        cv2.imwrite(save_file,frame)
        inumber +=1

cap.release()
cv2.destroyAllWindows()
