import cv2
import numpy as np
print("OpenCV Version : %s " % cv2.__version__)


img = cv2.imread("images/estadio.jpg")

drawing = False  # true if mouse is pressed
mode = True  # if True, draw normal line. Press 'm' to arrowed line
ix, iy = -1, -1


# mouse callback function
def draw_circle(event, x, y, flags, param):
    global ix, iy, drawing, mode, imgcopy, img

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
        imgcopy = img.copy()

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing is True:
            if mode is True:
                img = imgcopy.copy()
                cv2.line(img, (ix, iy), (x, y), (0, 0, 255), 15)
            else:
                cv2.circle(img, (x, y), 5, (0, 0, 255), -1)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        if mode is True:
            cv2.line(img, (ix, iy), (x, y), (0, 255, 0), 15)
        else:
            cv2.circle(img, (x, y), 5, (0, 0, 255), -1)


cv2.namedWindow('image')
cv2.setMouseCallback('image', draw_circle)

while(1):
    cv2.imshow('image', img)
    k = cv2.waitKey(1) & 0xFF
    if k == ord('m'):
        mode = not mode
    elif k == 27:
        break
