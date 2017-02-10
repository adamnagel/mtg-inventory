import cv2
import sys
import numpy as np
import cv2
import math

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
    cv2.imwrite('thresh.png', thresh)

    im2, contours, hier = cv2.findContours(thresh, cv2.RETR_LIST,
                                           cv2.CHAIN_APPROX_SIMPLE)

    return contours


# video_capture = cv2.VideoCapture(0)
while True:
    # Capture frame-by-frame
    # ret, frame = video_capture.read()
    # frame = cv2.imread('cache.png')
    frame = cv2.imread('50838297232__462D39E0-B9EB-46ED-BBD1-0D2F26D7E0B6.JPG')
    # cv2.imwrite('cache.png', frame)
    # exit(0)

    # smaller = cv2.resize(frame, (500, 500))

    contours = find_contours(frame)

    # consider
    # http://docs.opencv.org/trunk/dd/d49/tutorial_py_contour_features.html
    for idx, cnt in enumerate(contours):
        contour_area = cv2.contourArea(cnt)
        if SQUARE_THRESH_MAX > contour_area > SQUARE_THRESH_MIN:

            hull = cv2.convexHull(cnt)
            hull = cv2.approxPolyDP(hull,
                                    0.1 * cv2.arcLength(hull, True), True)
            if __name__ == '__main__':
                if len(hull) == 4:
                    print (idx, contour_area)
                    frame_w_contours = np.copy(frame)
                    cv2.drawContours(frame_w_contours, [hull], 0, (0, 255, 0), 2)

                    # Let's cut out just this part of the image
                    rect = cv2.minAreaRect(cnt)
                    box_ = cv2.boxPoints(rect)
                    box = np.int0(box_)
                    cv2.drawContours(frame_w_contours, [box], 0, (0, 0, 255), 2)

                    print (box)
                    print (rect)
                    # Let's find the rotation angle
                    # http://felix.abecassis.me/2011/10/opencv-rotation-deskewing/
                    angle = rect[2]
                    center = rect[0]
                    size = rect[1]

                    rot_mat = cv2.getRotationMatrix2D(center, angle, 1)
                    warp = cv2.warpAffine(frame, rot_mat,
                                          dsize=(frame.shape[1], frame.shape[0]),
                                          flags=cv2.INTER_CUBIC)

                    cv2.imwrite('warp{}.png'.format(idx), warp)

                    # Crop
                    cropped = cv2.getRectSubPix(warp,
                                                (int(size[0]), int(size[1])),
                                                (int(center[0]), int(center[1])))
                    cv2.imwrite('crop{}.png'.format(idx), cropped)

                    # Rotate to be upright
                    final_trans = cv2.transpose(cropped)
                    final = cv2.flip(final_trans, 0)
                    cv2.imwrite('final{}.png'.format(idx), final)

    cv2.imwrite('image.png', frame_w_contours)
    exit(0)

video_capture.release()
exit(0)
