import Tkinter as tk
import cv2
from PIL import Image, ImageTk

width, height = 800, 600
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

root = tk.Tk()
root.bind('<Escape>', lambda e: root.quit())
lmain = tk.Label(root)
lmain.pack()


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

    return contours, thresh


def show_frame():
    # Get a capture, keep only the frame
    _, frame = cap.read()

    # Render as color
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

    # Convert to PIL Image
    img_ = Image.fromarray(cv2image)
    img = img_.resize((400,300))
    imgtk = ImageTk.PhotoImage(image=img)

    # Add as member of lamin
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)

    # Call this function again after 100ms
    lmain.after(100, show_frame)


show_frame()
root.mainloop()
