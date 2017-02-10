import numpy as np
import cv2
import time

import sys
from PIL import Image
import pyocr
import pyocr.builders
import subprocess

pi = 3.14159

# A face-detection OpenCV example:
# https://realpython.com/blog/python/face-detection-in-python-using-a-webcam/

# Square detection:
# http://stackoverflow.com/questions/10533233/opencv-c-obj-c-advanced-square-detection

SQUARE_THRESH_MIN = 1000 * 1000
SQUARE_THRESH_MAX = 2 * 1000 * 1000


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


def find_card(frame):
    contours = find_contours(frame)

    # consider
    # http://docs.opencv.org/trunk/dd/d49/tutorial_py_contour_features.html
    for idx, cnt in enumerate(contours):
        contour_area = cv2.contourArea(cnt)
        frame_area = frame.size

        contour_proportion = contour_area / frame_area

        # if SQUARE_THRESH_MAX > contour_area > SQUARE_THRESH_MIN:
        if 0.05 < contour_proportion < 0.5:
            print (frame_area, contour_area, contour_proportion)

            hull = cv2.convexHull(cnt)
            hull = cv2.approxPolyDP(hull, 0.1 * cv2.arcLength(hull, True), True)
            if len(hull) == 4:
                # frame_w_contours = np.copy(frame)
                # cv2.drawContours(frame_w_contours, [hull], 0, (0, 255, 0), 2)

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
                cropped = cv2.getRectSubPix(warp,
                                            (int(size[0]), int(size[1])),
                                            (int(center[0]), int(center[1])))
                # cv2.imwrite('crop{}.png'.format(idx), cropped)

                # Rotate to be upright
                final_trans = cv2.transpose(cropped)
                final = cv2.flip(final_trans, 0)

                return final

    return None


def do_ocr(filename):
    # Try ocr
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        print("No OCR tool found")
        sys.exit(1)
    # The tools are returned in the recommended order of usage
    tool = tools[0]
    # print("Will use tool '%s'" % (tool.get_name()))
    # Ex: Will use tool 'libtesseract'

    img = Image.open(filename)
    line_and_word_boxes = tool.image_to_string(
        img, lang="eng",
        builder=pyocr.builders.LineBoxBuilder()
    )
    # for lwb in line_and_word_boxes:
    #     if lwb.content:
    #         print(lwb.word_boxes)
    #         print(lwb.content)
    #         print(lwb.position)
    #         print("==")

    img_height = img.size[1]
    for lwb in line_and_word_boxes:
        relpos = float(lwb.position[0][1]) / float(img_height)
        if lwb.content and relpos < 0.1:
            # print (relpos, img_height, lwb.position[0][1])
            print ("Possible title: ", lwb.content)
            # print(lwb.position)
            # print("==")


def handle_frame(frame):
    start = time.time()
    card = find_card(frame)
    if card is not None:
        filename = 'card.png'
        cv2.imwrite(filename, card)
        do_ocr(filename)

    print (time.time() - start)


# video_capture = cv2.VideoCapture(0)
while True:
    # Capture frame-by-frame
    # ret, frame = video_capture.read()
    frame_full = cv2.imread('50838297232__462D39E0-B9EB-46ED-BBD1-0D2F26D7E0B6.JPG')
    # handle_frame(frame)

    frame_half = cv2.resize(frame_full, dsize=(0, 0), fx=0.5, fy=0.5)
    frame_quarter = cv2.resize(frame_full, dsize=(0, 0), fx=0.25, fy=0.25)
    frame_eighth = cv2.resize(frame_full, dsize=(0, 0), fx=0.125, fy=0.125)

    frameset = [frame_full, frame_half, frame_quarter, frame_eighth]
    for f in frameset:
        handle_frame(f)

    exit(0)

video_capture.release()
exit(0)
