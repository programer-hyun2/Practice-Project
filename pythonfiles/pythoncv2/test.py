import cv2
file = 'image.jpg'
img = cv2.imread(file)
img = cv2.resize(img,(300,300))
gimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imshow("image",img)
cv2.imshow("image-gray",gimg)
cv2.waitKey(0)
cv2.destroyAllWindows()