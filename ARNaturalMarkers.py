import cv2
import numpy as np
print("OpenCV Version : %s " % cv2.__version__)


img = cv2.imread("images/estadio.jpg")

drawing = False  # true if mouse is pressed
mode = True  # if True, draw normal line. Press 'm' to arrowed line
ix, iy = -1, -1
thickness = 5


# mouse callback function
def draw_circle(event, x, y, flags, param):
    global ix, iy, drawing, mode, imgcopy, img

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
        imgcopy = img.copy()

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing is True:
            img = imgcopy.copy()
            if mode is True:
                cv2.line(img, (ix, iy), (x, y), (0, 0, 255), thickness)
            else:
                cv2.arrowedLine(img, (ix, iy), (x, y), (0, 0, 255), thickness)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        if mode is True:
            cv2.line(img, (ix, iy), (x, y), (0, 0, 255), thickness)
        else:
            cv2.arrowedLine(img, (ix, iy), (x, y), (0, 0, 255), thickness)


cv2.namedWindow('image')
cv2.setMouseCallback('image', draw_circle)

while(1):
    cv2.imshow('image', img)
    k = cv2.waitKey(1) & 0xFF
    if k == ord('m'):
        mode = not mode
    elif k == ord('2'):
        thickness += 1
    elif k == ord('1'):
            thickness -= 1
    elif k == 27:
        break
