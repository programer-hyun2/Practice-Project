import cv2
def apply_blur(image_path, x, y, width, height, ksize=(15, 15)):
    image = cv2.imread(image_path)
    roi = image[y:y+height, x:x+width]
    blurred_roi = cv2.GaussianBlur(roi, ksize, 0)
    image[y:y+height, x:x+width] = blurred_roi
    cv2.imshow("Blurred Image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


apply_blur("images\images1.jpg", 50, 50, 200, 200)