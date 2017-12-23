import cv2
import numpy as np
from tkinter.filedialog import askopenfilenames
from tkinter import Tk
import pickle
import os
from Classes import Mode, RectangularObj, CircleObj, TextObj, Subset, Image


def crop_image(img, x1, y1, x2, y2):
    if x1 < x2 and y1 < y2:
        return img[y1:y2, x1:x2].copy()
    elif x1 < x2 and y1 > y2:
        return img[y2:y1, x1:x2].copy()
    elif x1 > x2 and y1 < y2:
        return img[y1:y2, x2:x1].copy()
    elif x1 > x2 and y1 > y2:
        return img[y2:y1, x2:x2].copy()


# mouse callback function
def draw_circle(event, x, y, flags, param):
    global ix, iy, drawing, mode, imgcopy, img, font_size, imgList, subsets

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
        imgcopy = img.copy()

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing is True:
            img = imgcopy.copy()
            if mode == Mode.RECTANGLE:
                cv2.rectangle(img, (ix, iy), (x, y), (0, 0, 255), thickness)
            elif mode == Mode.CIRCLE:
                a = np.array((ix, iy))
                b = np.array((x, y))
                dist = np.linalg.norm(a - b)
                cv2.circle(img, (ix, iy), int(dist), (0, 255, 0), thickness)

    elif event == cv2.EVENT_LBUTTONDBLCLK:
        if mode == Mode.ARROW:
            cv2.arrowedLine(img, (x, y - 50), (x, y), (0, 0, 255), thickness)
            subsets.append(Subset(Mode.ARROW,
                           RectangularObj((x, y - 50),
                                          (x, y),
                                          (0, 0, 255),
                                          thickness),
                           crop_image(imgList[0], x - 50, y - 50, x + 50, y)))

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        if mode == Mode.RECTANGLE:
            cv2.rectangle(img, (ix, iy), (x, y), (0, 0, 255), thickness)
            subsets.append(Subset(mode,
                           RectangularObj((ix, iy),
                                          (x, y),
                                          (0, 0, 255),
                                          thickness),
                           crop_image(imgList[0], ix, iy, x, y)))
        elif mode == Mode.CIRCLE:
            a = np.array((ix, iy))
            b = np.array((x, y))
            dist = np.linalg.norm(a - b)
            cv2.circle(img, (ix, iy), int(dist), (0, 0, 255), thickness)
            subsets.append(Subset(mode,
                           CircleObj((ix, iy),
                                     int(dist),
                                     (0, 0, 255),
                                     thickness),
                           crop_image(imgList[0], ix - int(dist), iy - int(dist),
                                      ix + int(dist), iy + int(dist))))
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

                subsets.append(Subset(Mode.TEXT,
                               TextObj(RectangularObj((x, y),
                                                      (x + ix, y - iy),
                                                      (255, 255, 255),
                                                      -1),
                                       s[:-1], font_size, 255, 1),
                               crop_image(imgList[0],
                                          x - 20, y + 20,
                                          x + ix + 20, y - iy - 20)))
                break
        imgList.append(img.copy())


window = Tk()
files = askopenfilenames()
filenames = window.tk.splitlist(files)
window.withdraw()

if os.path.exists('imagesdb.obj') and os.path.getsize('imagesdb.obj') > 0:
    images = pickle.load(open("imagesdb.obj", "rb"))
else:
    images = []


for filename in filenames:
    img = cv2.imread(filename)

    drawing = False  # true if mouse is pressed
    mode = Mode.ARROW
    ix, iy = -1, -1
    thickness = 5
    font_size = 1
    imgList = [img.copy()]
    subsets = []

    cv2.namedWindow('image')
    cv2.setMouseCallback('image', draw_circle)

    while(1):
        cv2.imshow('image', img)
        k = cv2.waitKey(1) & 0xFF
        if k == ord('m'):
            if mode.value < 3:
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
                subsets.pop()
        elif k == 27:
            cv2.destroyAllWindows()
            print('Preparation canceled for this image.')
            break
        elif k == ord('s'):
            cv2.destroyAllWindows()
            print('Preparation done. Saving...')
            newfilename = os.path.splitext(os.path.basename(filename))[0] + ".png"
            cv2.imwrite(os.path.join('prepared', newfilename), img)
            if(any(image.filename == newfilename for image in images)):
                index = next((i for i, image in enumerate(images)
                             if image.filename == newfilename), -1)
                images[index] = Image(imgList[0], newfilename, subsets)
            else:
                images.append(Image(imgList[0], newfilename, subsets))
            break

if len(images) > 0:
    pickle.dump(images, open("imagesdb.obj", "wb"))
    print('Saved images to database!')
else:
    print('No images to save. Exiting...')
