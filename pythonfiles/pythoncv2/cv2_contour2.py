import cv2
import os

os.system("cls")
file = 'images\image4.jpg'

img = cv2.imread(file)
imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

_, imgThreshold = cv2.threshold(imgGray,20,255,cv2.THRESH_BINARY_INV)

contour, _ = cv2.findContours(imgThreshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

imgContour = cv2.drawContours(img, contour, -1, (0,255,255),5)

c = max(contour, key = cv2.contourArea)

x, y, w, h = cv2.boundingRect(c)
print(x,y,w,h)

cv2.rectangle(imgContour, (x, y), (x+w, y+h), (255, 255, 0), 5)

cv2.imshow("Original", img)
cv2.imshow("Contour", imgContour)

cv2.waitKey(0)

cv2.destroyAllWindows()
