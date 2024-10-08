import cv2
import numpy as np
import os

os.system("cls")

def bitwise_nand(img1,img2):
    return cv2.bitwise_not(cv2.bitwise_and(img1,img2))

def bitwise_nor(img1,img2):
    return cv2.bitwise_not(cv2.bitwise_or(img1,img2))

def bitwise_xnor(img1,img2):
    return cv2.bitwise_not(cv2.bitwise_xor(img1,img2))

rectangle = np.zeros((300,300),dtype="uint8")
circle = np.zeros((300,300),dtype="uint8")

x,y,w,h,r = 25,25,250,250,150
center = (150,150)

cv2.rectangle(rectangle,(x,y),(x+w,y+h),255,-1)
cv2.circle(circle, center,r,255,-1)

img_and = cv2.bitwise_and(circle,rectangle)
img_or = cv2.bitwise_or(circle,rectangle)
img_not = cv2.bitwise_not(circle)
img_xor = cv2.bitwise_xor(circle,rectangle)
img_nand = bitwise_nand(circle,rectangle)
img_nor = bitwise_nor(circle,rectangle)
img_xnor = bitwise_xnor(circle,rectangle)

cv2.imshow("Rectangle",rectangle)
cv2.imshow("Circle",circle)
cv2.imshow("and",img_and)
cv2.imshow("or",img_or)
cv2.imshow("not",img_not)
cv2.imshow("xor",img_xor)
cv2.imshow("nand",img_nand)
cv2.imshow("nor",img_nor)
cv2.imshow("xnor",img_xnor)

cv2.waitKey(0)
cv2.destroyAllWindows