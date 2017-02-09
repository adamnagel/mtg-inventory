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

def accept_line_pair(line1, line2, minTheta):
    theta1 = line1[0][1]
    theta2 = line2[0][1]

    if theta1 < minTheta:
        theta1 += pi
    if theta2 < minTheta:
        theta2 += pi

    return abs(theta1 - theta2) > minTheta


class Point2f:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def line_to_point_pair(line):
    points = list()

    r = line[0][0]
    t = line[0][1]
    cos_t = math.cos(t)
    sin_t = math.sin(t)
    x0 = r * cos_t
    y0 = r * sin_t
    alpha = 1000

    points.insert(0, Point2f(x0 + alpha * (-sin_t),
                             y0 + alpha * cos_t))
    points.insert(0, Point2f(x0 - alpha * (-sin_t),
                             y0 - alpha * cos_t))

    return points


def compute_intersect(line1, line2):
    p1 = line_to_point_pair(line1)
    p2 = line_to_point_pair(line2)

    denom = (p1[0].x - p1[1].x) * (p2[0].y - p2[1].y) - (p1[0].y - p1[1].y) * (p2[0].x - p2[1].x)

    intersect = Point2f(((p1[0].x * p1[1].y - p1[0].y * p1[1].x) * (p2[0].x - p2[1].x) -
                         (p1[0].x - p1[1].x) * (p2[0].x * p2[1].y - p2[0].y * p2[1].x))
                        / denom,
                        ((p1[0].x * p1[1].y - p1[0].y * p1[1].x) * (p2[0].y - p2[1].y) -
                         (p1[0].y - p1[1].y) * (p2[0].x * p2[1].y - p2[0].y * p2[1].x))
                        / denom)

    return intersect


video_capture = cv2.VideoCapture(0)
while True:
    # Capture frame-by-frame
    # ret, frame = video_capture.read()
    frame = cv2.imread('cache.png')
    # cv2.imwrite('cache.png', frame)
    # exit(0)

    # Convert to gray
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Thresh
    # http://docs.opencv.org/3.1.0/d7/d4d/tutorial_py_thresholding.html
    gblur = cv2.GaussianBlur(gray, (5, 5), 0)
    retval, thresh = cv2.threshold(gblur, 0, 255,
                                   cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Detect edges and lines
    edges = cv2.Canny(thresh, 66.0, 133.0, 3)
    lines = cv2.HoughLines(edges, 1, pi / 180, 50, 0, 0)
    # print ("Detected " + str(len(lines)) + " lines")

    tosave = edges

    if lines is None:
        continue

    intersections = list()
    for line1 in lines:
        for line2 in lines:
            if accept_line_pair(line1, line2, pi / 32):
                intersection = compute_intersect(line1, line2)
                intersections.insert(0, intersection)

    circled = frame
    for idx, intersection in enumerate(intersections):
        cv2.circle(circled,
                   (int(intersection.x), int(intersection.y)),
                   1, (0, 0, 255), 3)
        tosave = circled

    # corners = cv2.goodFeaturesToTrack(gray, 25, 0.01, 10)
    # corners = np.int0(corners)
    # for i in corners:
    #     x, y = i.ravel()
    #     cv2.circle(frame, (x, y), 3, 255, -1)

    # write the frame for debugging
    cv2.imwrite('image.png', tosave)
    exit(0)

video_capture.release()
exit(0)
