import cv2
import numpy as np
from tkinter.filedialog import askopenfilename
from tkinter import Tk
import pickle
import os
from Classes import Mode, RectangularObj, CircleObj, TextObj, Subset, Image


window = Tk()
filename = askopenfilename()
window.withdraw()

if os.path.exists('imagesdb.obj') and os.path.getsize('imagesdb.obj') > 0:
    images = pickle.load(open("imagesdb.obj", "rb"))
else:
    exit()
    print("ERROR: Database not found. Exiting...")

print(images[0].filename)
# start match
img = cv2.imread(filename)

sift = cv2.xfeatures2d.SIFT_create()
bf = cv2.BFMatcher()

kp, des = sift.detectAndCompute(img, None)

# Detect images in db with enough good matches
for image in images:
    image.kp, image.des = sift.detectAndCompute(image.img, None)
    image.matches = bf.knnMatch(image.des, des, k=2)

    num_rows, num_cols = image.des.shape

    image.good_matches = []
    for m, n in image.matches:
        if m.distance < 0.75 * n.distance:
            image.good_matches.append(m)
    if len(image.good_matches) <= 60:
        images.remove(image)

if len(images) <= 0:
    print("No images found. Exiting...")
    exit()

# Choose the best one
bestIndex = -1

for i, image in enumerate(images):
    if bestIndex == -1:
        bestIndex == i
    elif len(image.good_matches) > len(images[i].good_matches):
        bestIndex == i

image = images[0]
# Detect keypoints, matches and good matches from subsets
for subset in image.subsets:
    subset.kp, subset.des = sift.detectAndCompute(subset.img, None)

    subset.matches = bf.knnMatch(subset.des, des, k=2)

    num_rows, num_cols = subset.des.shape

    subset.good_matches = []
    for m, n in subset.matches:
        if m.distance < 0.75 * n.distance:
            subset.good_matches.append(m)


# Keypoints from good matches
for subset in image.subsets:
    subset.subpt = []
    subset.imgpt = []
    for good_match in subset.good_matches:
        subset.subpt.append(subset.kp[good_match.queryIdx].pt)
        subset.imgpt.append(kp[good_match.trainIdx].pt)

# Remove subset without enough points
for subset in image.subsets:
    if len(subset.subpt) == 0 or len(subset.imgpt) == 0:
        image.subsets.remove(subset)

# Homography
for subset in image.subsets:
    subset.homography, mask = cv2.findHomography(np.asarray(subset.subpt),
                                                 np.asarray(subset.imgpt),
                                                 cv2.RANSAC)
    num_rows, num_cols = subset.homography.shape
    if num_rows == 0 or num_cols == 0:
        image.subsets.remove(subset)

for subset in image.subsets:
    h, w, _ = subset.img.shape
    pts = np.float32([[0, 0], [0, h - 1],
                     [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
    subset.subcorners = pts

for subset in image.subsets:
    subset.imgcorners = cv2.perspectiveTransform(subset.subcorners,
                                                 subset.homography)

# Display
for subset in image.subsets:
    if subset.mode == Mode.ARROW:
        print(subset.imgcorners)
        print(subset.imgcorners[0, 0][0])
        ix = int(subset.imgcorners[0, 0][0])
        iy = int(subset.imgcorners[0, 0][1])
        w = int(subset.imgcorners[2, 0][0]) - ix
        h = int(subset.imgcorners[2, 0][1]) - iy

        cv2.arrowedLine(img, (ix + int(w / 2), iy),
                             (ix + int(w / 2), iy + int(h / 2) + 25),
                             (0, 0, 255), subset.obj.thickness)
    elif subset.mode == Mode.RECTANGLE:
        print(subset.imgcorners)
        print(subset.imgcorners[0, 0][0])
        ix = int(subset.imgcorners[0, 0][0])
        iy = int(subset.imgcorners[0, 0][1])
        x = int(subset.imgcorners[2, 0][0])
        y = int(subset.imgcorners[2, 0][1])

        cv2.rectangle(img, (ix, iy), (x, y),
                           (0, 0, 255), subset.obj.thickness)

    elif subset.mode == Mode.TEXT:
        print(subset.imgcorners)
        print(subset.imgcorners[0, 0][0])
        x = int(subset.imgcorners[1, 0][0]) + 20
        y = int(subset.imgcorners[1, 0][1]) - 20
        text = cv2.getTextSize(subset.obj.text, cv2.FONT_HERSHEY_SIMPLEX,
                               subset.obj.font_size, 1)[0]
        ix, iy = text

        cv2.rectangle(img, (x, y), (x + ix, y - iy),
                           (255, 255, 255), -1)
        cv2.putText(img, subset.obj.text, (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, subset.obj.font_size,
                    255, 1)

    elif subset.mode == Mode.CIRCLE:
        print(subset.imgcorners)
        print(subset.imgcorners[0, 0][0])
        ix = int(subset.imgcorners[0, 0][0])
        iy = int(subset.imgcorners[0, 0][1])
        w = int(subset.imgcorners[2, 0][0]) - ix

        cv2.circle(img, (ix + int(w / 2), iy + int(w / 2)), int(w / 2),
                        (0, 0, 255), subset.obj.thickness)


cv2.namedWindow('image')
cv2.imshow('image', img)

newfilename = os.path.splitext(os.path.basename(filename))[0] + ".png"
cv2.imwrite(os.path.join('augmented', newfilename), img)

