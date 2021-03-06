import cv2
import numpy as np
from tkinter.filedialog import askopenfilename
from tkinter import Tk
import pickle
import os
import sys
from Classes import Mode, RectangularObj, CircleObj, TextObj, Subset, Image


window = Tk()
filename = askopenfilename()
window.withdraw()

if len(sys.argv) > 1 and sys.argv[1] == 'debug':
    debug = True
else:
    debug = False

if os.path.exists('imagesdb.obj') and os.path.getsize('imagesdb.obj') > 0:
    images = pickle.load(open("imagesdb.obj", "rb"))
else:
    exit()
    print("ERROR: Database not found. Exiting...")

# start match
img = cv2.imread(filename)
if debug:
    print('Image loaded.')

sift = cv2.xfeatures2d.SIFT_create()
bf = cv2.BFMatcher()

kp, des = sift.detectAndCompute(img, None)
if debug:
    print('Detected image keypoints and descripts from image.')

if debug:
    print('There are ', len(images), ' images on database.')
    print('Detecting images with enough good matches...')

good_images = images.copy()
# Detect images in db with enough good matches
for i, image in enumerate(images):
    image.kp, image.des = sift.detectAndCompute(image.img, None)
    image.matches = bf.knnMatch(image.des, des, k=2)

    num_rows, num_cols = image.des.shape

    image.good_matches = []
    for m, n in image.matches:
        if m.distance < 0.75 * n.distance:
            image.good_matches.append(m)
    if debug:
        print('Database image #', i, ' has ',
              len(image.good_matches), ' good matches.')
    if len(image.good_matches) <= 60:
        if debug:
            print('Database image #', i, ' doesn\'t have enough matches. Removed.')
        good_images.remove(image)
    else:
        if debug:
            print('Database image #', i, ' has enough good matches.')

if len(good_images) <= 0:
    print("No images found. Exiting...")
    exit()

if debug:
    print('Found ', len(good_images), ' images with enough good matches.')
    print('Choosing the best one...')

# Choose the best one
bestIndex = -1

for i, image in enumerate(good_images):
    if bestIndex == -1:
        bestIndex = i
    elif len(image.good_matches) > len(good_images[bestIndex].good_matches):
        bestIndex = i

image = good_images[bestIndex]
if debug:
    print('Found best image  ,', bestIndex)
    print('Detecting all keypoints, descriptors and good matches from subsets...')

# Detect keypoints, matches and good matches from subsets
for subset in image.subsets:
    subset.kp, subset.des = sift.detectAndCompute(subset.img, None)

    subset.matches = bf.knnMatch(subset.des, des, k=2)

    num_rows, num_cols = subset.des.shape

    subset.good_matches = []
    for m, n in subset.matches:
        if m.distance < 0.75 * n.distance:
            subset.good_matches.append(m)

if debug:
    print('Detecting all points from good matches...')

# Keypoints from good matches
for subset in image.subsets:
    subset.subpt = []
    subset.imgpt = []
    for good_match in subset.good_matches:
        subset.subpt.append(subset.kp[good_match.queryIdx].pt)
        subset.imgpt.append(kp[good_match.trainIdx].pt)

if debug:
    print('Removing subsets without enough points...')
# Remove subset without enough points
for subset in image.subsets:
    if len(subset.subpt) == 0 or len(subset.imgpt) == 0:
        image.subsets.remove(subset)

if debug:
    print('Applying homography between each subset and image...')
# Homography
for subset in image.subsets:
    subset.homography, mask = cv2.findHomography(np.asarray(subset.subpt),
                                                 np.asarray(subset.imgpt),
                                                 cv2.RANSAC)
    num_rows, num_cols = subset.homography.shape
    if num_rows == 0 or num_cols == 0:
        image.subsets.remove(subset)

if debug:
    print('Getting corners in original image...')
# Get corner points in original cropped image
for subset in image.subsets:
    h, w, _ = subset.img.shape
    pts = np.float32([[0, 0], [0, h - 1],
                     [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
    subset.subcorners = pts

if debug:
    print('Applying perspective transform...')
# Apply perspective transform to get corners in image
for subset in image.subsets:
    subset.imgcorners = cv2.perspectiveTransform(subset.subcorners,
                                                 subset.homography)

if debug:
    print('Display started...')
# Display
for subset in image.subsets:
    if subset.mode == Mode.ARROW:
        ix = int(subset.imgcorners[0, 0][0])
        iy = int(subset.imgcorners[0, 0][1])
        w = int(subset.imgcorners[2, 0][0]) - ix
        h = int(subset.imgcorners[2, 0][1]) - iy

        cv2.arrowedLine(img, (ix + int(w / 2), iy),
                             (ix + int(w / 2), iy + int(h / 2) + 25),
                             (0, 0, 255), subset.obj.thickness)
        if debug:
            print('Arrow displayed.')
    elif subset.mode == Mode.RECTANGLE:
        ix = int(subset.imgcorners[0, 0][0])
        iy = int(subset.imgcorners[0, 0][1])
        x = int(subset.imgcorners[2, 0][0])
        y = int(subset.imgcorners[2, 0][1])

        cv2.rectangle(img, (ix, iy), (x, y),
                           (0, 0, 255), subset.obj.thickness)
        if debug:
            print('Rectangle displayed.')

    elif subset.mode == Mode.TEXT:
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
        if debug:
            print('Text displayed.')

    elif subset.mode == Mode.CIRCLE:
        ix = int(subset.imgcorners[0, 0][0])
        iy = int(subset.imgcorners[0, 0][1])
        w = int(subset.imgcorners[2, 0][0]) - ix

        cv2.circle(img, (ix + int(w / 2), iy + int(w / 2)), int(w / 2),
                        (0, 0, 255), subset.obj.thickness)
        if debug:
            print('Circle displayed.')

if debug:
    print('Display finished!')


cv2.namedWindow('image')
cv2.imshow('image', img)

newfilename = os.path.splitext(os.path.basename(filename))[0] + ".png"
cv2.imwrite(os.path.join('augmented', newfilename), img)
print('Augmented image is on \'augmented\' folder.')
