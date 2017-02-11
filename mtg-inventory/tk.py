from Tkinter import *
import cv2
from PIL import Image, ImageTk
import numpy as np
import time
import pyocr
import pyocr.builders


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
                frame_w_contours = np.copy(frame)
                cv2.drawContours(frame_w_contours, [hull], 0, (0, 255, 0), 2)
                # cv2.imwrite('contours.png', frame_w_contours)

                # Let's cut out just this part of the image
                rect = cv2.minAreaRect(cnt)
                # box_ = cv2.boxPoints(rect)
                # box = np.int0(box_)
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

                return final, frame_w_contours

    return None, None


def do_ocr(img):
    # Try ocr
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        print("No OCR tool found")
        # sys.exit(1)
    # print("OCR")
    # The tools are returned in the recommended order of usage
    tool = tools[0]
    # print("Will use tool '%s'" % (tool.get_name()))
    # Ex: Will use tool 'libtesseract'

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
        print (relpos, lwb.content)
        if lwb.content and relpos < 0.2:
            # print (relpos, img_height, lwb.position[0][1])
            print ("Possible title: ", lwb.content)
            # print(lwb.position)
            # print("==")


class App:
    def __init__(self, master):
        frame = Frame(master)
        frame.pack()

        self.raw_img = Label(master)
        self.raw_img.pack(side=TOP)

        self.thresh = Label(master)
        self.thresh.pack(side=TOP)

        self.card = Label(master)
        self.card.pack(side=BOTTOM)

        self.contours = Label(master)
        self.contours.pack(side=LEFT)

        self.button = Button(frame, text="QUIT", fg="red", command=frame.quit)
        self.button.pack(side=BOTTOM)

        self.cap = None
        self.start_cap()

        self.show_frame()

    def start_cap(self):
        # width, height = 800, 600
        self.cap = cv2.VideoCapture(0)
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def show_frame(self):
        # Get a capture, keep only the frame
        _, frame = self.cap.read()

        # Render as color
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

        # Convert to PIL Image
        img_ = Image.fromarray(cv2image)
        img = img_.resize((400, 300))
        imgtk = ImageTk.PhotoImage(image=img)
        # cv2.imwrite('close.png', frame)

        # Add as member of raw_img
        self.raw_img.imgtk = imgtk
        self.raw_img.configure(image=imgtk)

        # Do contour
        # contours, thresh = find_contours(frame)
        # timg_ = Image.fromarray(thresh)
        # timg = timg_.resize((400, 300))
        # timgtk = ImageTk.PhotoImage(image=timg)
        #
        # self.thresh.imgtk = timgtk
        # self.thresh.configure(image=timgtk)

        # Find card
        card, frame_with_contours = find_card(frame)
        if card is not None:
            # print (str(time.time()) +
            cimg_ = Image.fromarray(card)
            cimg = cimg_
            cimgtk = ImageTk.PhotoImage(image=cimg)

            do_ocr(cimg_)

            self.card.imgtk = cimgtk
            self.card.configure(image=cimgtk)

            cont_img = Image.fromarray(frame_with_contours).resize((400, 300))
            cont_imgtk = ImageTk.PhotoImage(image=cont_img)

            self.contours.imgtk = cont_imgtk
            self.contours.configure(image=cont_imgtk)

        # Call this function again after 100ms
        self.raw_img.after(100, self.show_frame)


root = Tk()
app = App(root)
root.mainloop()
root.destroy()
