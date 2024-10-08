import cv2
import numpy as np
red = [38,17,206]
blue = [104,40,0]
white = [255,255,255]

def solution(img):
    img[0:50,:] = red
    img[50:150,:] = blue
    img[150:200,:] = red
    cv2.circle(img,(150,100),40,white,-1)

img1 = np.zeros((200,300,3),dtype="uint8")    
solution(img1)
cv2.imshow("image",img1)
cv2.waitKey(0)
cv2.destroyAllWindows()

