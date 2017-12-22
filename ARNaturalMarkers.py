import cv2
import numpy as np
from enum import Enum
from tkinter.filedialog import askopenfilenames
from tkinter import Tk


class Mode(Enum):
    LINE = 1
    ARROW = 2
    RECTANGLE = 3
    CIRCLE = 4


# mouse callback function
def draw_circle(event, x, y, flags, param):
    global ix, iy, drawing, mode, imgcopy, img, font_size, imgList

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
        imgcopy = img.copy()

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing is True:
            img = imgcopy.copy()
            if mode == Mode.LINE:
                cv2.line(img, (ix, iy), (x, y), (0, 0, 255), thickness)
            elif mode == Mode.ARROW:
                cv2.arrowedLine(img, (ix, iy), (x, y), (0, 0, 255), thickness)
            elif mode == Mode.RECTANGLE:
                cv2.rectangle(img, (ix, iy), (x, y), (0, 0, 255), thickness)
            elif mode == Mode.CIRCLE:
                a = np.array((ix, iy))
                b = np.array((x, y))
                dist = np.linalg.norm(a - b)
                cv2.circle(img, (ix, iy), int(dist), (0, 255, 0), thickness)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        if mode == Mode.LINE:
            cv2.line(img, (ix, iy), (x, y), (0, 0, 255), thickness)
        elif mode == Mode.ARROW:
            cv2.arrowedLine(img, (ix, iy), (x, y), (0, 0, 255), thickness)
        elif mode == Mode.RECTANGLE:
            cv2.rectangle(img, (ix, iy), (x, y), (0, 0, 255), thickness)
        elif mode == Mode.CIRCLE:
            a = np.array((ix, iy))
            b = np.array((x, y))
            dist = np.linalg.norm(a - b)
            cv2.circle(img, (ix, iy), int(dist), (0, 0, 255), thickness)
        imgList.append(img.copy())

    elif event == cv2.EVENT_RBUTTONDOWN:
        s = ""
        imgcopy = img.copy()
        while(1):
            k = cv2.waitKey(0) & 0xFF
            if k != 27:
                s += chr(k)
            print(s)
            if k == 9:
                text = cv2.getTextSize(s[:-1], cv2.FONT_HERSHEY_SIMPLEX,
                                       font_size, 1)[0]
                ix, iy = text
                cv2.rectangle(img, (x, y), (x + ix, y - iy),
                              (255, 255, 255), -1)
                cv2.putText(img, s[:-1], (x, y),
                            cv2.FONT_HERSHEY_SIMPLEX, font_size,
                            255, 1)
                break
        imgList.append(img.copy())


window = Tk()
files = askopenfilenames()
filenames = window.tk.splitlist(files)

for filename in filenames:
    img = cv2.imread(filename)

    drawing = False  # true if mouse is pressed
    mode = Mode.LINE  # if True, draw normal line. Press 'm' to arrowed line
    ix, iy = -1, -1
    thickness = 5
    font_size = 1
    imgList = [img.copy()]

    cv2.namedWindow('image')
    cv2.setMouseCallback('image', draw_circle)

    while(1):
        cv2.imshow('image', img)
        k = cv2.waitKey(1) & 0xFF
        if k == ord('m'):
            if mode.value < len(Mode):
                mode = Mode(mode.value + 1)
            else:
                mode = Mode(1)
        elif k == ord('2'):
            thickness += 1
        elif k == ord('1'):
                thickness -= 1
        elif k == ord('4'):
            font_size += 0.1
        elif k == ord('3'):
            font_size -= 0.1
        elif k == 8:
            if(len(imgList) > 1):
                imgList.pop()
                img = imgList[len(imgList) - 1]
        elif k == 27:
            cv2.destroyAllWindows()
            break
