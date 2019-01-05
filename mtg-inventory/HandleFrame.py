import numpy as np
import cv2
import time

import sys
from PIL import Image
# import pyocr
# import pyocr.builders
import subprocess

from CardMatcher import CardMatcher
from CardLookup import CardLookup

pi = 3.14159


# A face-detection OpenCV example:
# https://realpython.com/blog/python/face-detection-in-python-using-a-webcam/

# Square detection:
# http://stackoverflow.com/questions/10533233/opencv-c-obj-c-advanced-square-detection

def permute(image):
    image90 = rotate_bound(image, 90)
    image180 = rotate_bound(image, 180)
    image270 = rotate_bound(image, 270)

    return [image, image90, image180, image270]


def find_contours(frame):
    # Convert to gray
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Thresh
    # http://docs.opencv.org/3.1.0/d7/d4d/tutorial_py_thresholding.html
    gblur = cv2.GaussianBlur(gray, (5, 5), 0)
    retval, thresh = cv2.threshold(gblur, 0, 255,
                                   cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # cv2.imwrite('thresh.png', thresh)

    im2, contours, hier = cv2.findContours(thresh, cv2.RETR_LIST,
                                           cv2.CHAIN_APPROX_SIMPLE)

    return contours


def rotate_bound(image, angle):
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)

    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    # perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (nW, nH))


def find_card(frame):
    contours = find_contours(frame)

    # consider
    # http://docs.opencv.org/trunk/dd/d49/tutorial_py_contour_features.html
    for idx, cnt in enumerate(contours):
        contour_area = cv2.contourArea(cnt)
        frame_area = frame.size

        contour_proportion = contour_area / frame_area

        # if SQUARE_THRESH_MAX > contour_area > SQUARE_THRESH_MIN:
        if 0.01 < contour_proportion < 0.75:
            print(frame_area, contour_area, contour_proportion)

            hull = cv2.convexHull(cnt)
            hull = cv2.approxPolyDP(hull, 0.1 * cv2.arcLength(hull, True), True)
            if len(hull) == 4:
                frame_w_contours = np.copy(frame)
                cv2.drawContours(frame_w_contours, [hull], 0, (0, 255, 0), 2)
                # cv2.imwrite('contour{}.png'.format(idx), frame_w_contours)
                cv2.imshow('contour', frame_w_contours)

                # Let's cut out just this part of the image
                rect = cv2.minAreaRect(cnt)
                box_ = cv2.boxPoints(rect)
                box = np.int0(box_)
                # cv2.drawContours(frame_w_contours, [box], 0, (0, 0, 255), 2)

                # Let's find the rotation angle
                # http://felix.abecassis.me/2011/10/opencv-rotation-deskewing/
                angle = rect[2]
                center = rect[0]
                size = rect[1]

                rot_mat = cv2.getRotationMatrix2D(center, angle, 1)
                warp = cv2.warpAffine(frame, rot_mat,
                                      dsize=(frame.shape[1], frame.shape[0]),
                                      flags=cv2.INTER_CUBIC)
                # cv2.imwrite('warp{}.png'.format(idx), warp)

                # Crop
                trim_factor = 0.95
                cropped = cv2.getRectSubPix(warp,
                                            (int(size[0] * trim_factor), int(size[1] * trim_factor)),
                                            (int(center[0]), int(center[1])))
                # cv2.imwrite('crop{}.png'.format(idx), cropped)

                # Rotate to be upright
                final_trans = cv2.transpose(cropped)
                final = cv2.flip(final_trans, 0)
                # cv2.imwrite('final.png', final)

                return final

    return None


class HandleFrame(object):
    def __init__(self):
        self.cm = CardMatcher()
        self.cl = CardLookup()

    SQUARE_THRESH_MIN = 1000 * 1000
    SQUARE_THRESH_MAX = 2 * 1000 * 1000

    def handle_frame(self, frame):
        start = time.time()
        card = find_card(frame)

        best_id = None
        best_quality = None

        if card is not None:
            for orientation in permute(card):
                filename = 'card.png'
                cv2.imwrite(filename, orientation)

                id, quality = self.cm.MatchCardImg(orientation)

                print('{} {} {}'.format(quality, self.cl.lookup(id)['name'], id))

                if not best_quality or quality < best_quality:
                    best_quality = quality
                    best_id = id

            print(time.time() - start)

            # data = cl.lookup(best_id)
            # print('I think this is {}'.format(data['name']))

            # video_capture = cv2.VideoCapture(0)

        return best_id, best_quality

    def handle_frame_img(self, path_img):
        frame_full = cv2.imread(path_img)
        return self.handle_frame(frame_full)
