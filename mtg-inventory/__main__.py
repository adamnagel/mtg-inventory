import cv2
import sys
import numpy as np
import cv2

# A face-detection OpenCV example:
# https://realpython.com/blog/python/face-detection-in-python-using-a-webcam/

# Square detection:
# http://stackoverflow.com/questions/10533233/opencv-c-obj-c-advanced-square-detection

video_capture = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    # Convert to gray
    blur = cv2.medianBlur(frame, 5)
    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255,
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY,
                                   11, 2)

    gblur = cv2.GaussianBlur(gray, (5, 5), 0)
    retval, otsu = cv2.threshold(gblur, 0, 255,
                                 cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imwrite('otsu.png', otsu)

    tosave = thresh

    # corners = cv2.goodFeaturesToTrack(gray, 25, 0.01, 10)
    # corners = np.int0(corners)
    # for i in corners:
    #     x, y = i.ravel()
    #     cv2.circle(frame, (x, y), 3, 255, -1)

    # write the frame for debugging
    cv2.imwrite('image.png', tosave)

video_capture.release()
exit(0)
