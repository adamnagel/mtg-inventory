import cv2
import sys

# A face-detection OpenCV example:
# https://realpython.com/blog/python/face-detection-in-python-using-a-webcam/


video_capture = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    # Now we have the frame!

    # write the frame for debugging
    cv2.imwrite('image.png', frame)

video_capture.release()
exit(0)
