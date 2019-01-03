import numpy as np
import cv2
from CardMatcher import CardMatcher
from CardLookup import CardLookup
from os.path import join, dirname


# https://github.com/hj3yoo/mtg_card_detector/blob/master/opencv_dnn.py
def order_points(pts):
    """
    initialzie a list of coordinates that will be ordered such that the first entry in the list is the top-left,
    the second entry is the top-right, the third is the bottom-right, and the fourth is the bottom-left
    :param pts: array containing 4 points
    :return: ordered list of 4 points
    """
    rect = np.zeros((4, 2), dtype="float32")

    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    # return the ordered coordinates
    return rect


def four_point_transform(image, pts):
    """
    Transform a quadrilateral section of an image into a rectangular area
    From: www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/
    :param image: source image
    :param pts: 4 corners of the quadrilateral
    :return: rectangular image of the specified area
    """
    # obtain a consistent order of the points and unpack them
    # individually
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    # compute the perspective transform matrix and then apply it
    mat = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, mat, (maxWidth, maxHeight))

    # If the image is horizontally long, rotate it by 90
    if maxWidth > maxHeight:
        center = (maxHeight / 2, maxHeight / 2)
        mat_rot = cv2.getRotationMatrix2D(center, 270, 1.0)
        warped = cv2.warpAffine(warped, mat_rot, (maxHeight, maxWidth))

    # return the warped image
    return warped


def find_card(img, thresh_c=5, kernel_size=(3, 3), size_thresh=20000):
    # preprocessing - grayscale, blurring, thresholding
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.medianBlur(img_gray, 5)
    img_thresh = cv2.adaptiveThreshold(img_blur,
                                       255,
                                       cv2.ADAPTIVE_THRESH_MEAN_C,
                                       cv2.THRESH_BINARY_INV,
                                       5,
                                       thresh_c)

    # Dilute the image, then erode to remove minor noise
    kernel = np.ones(kernel_size, np.uint8)
    img_dilate = cv2.dilate(img_thresh, kernel, iterations=1)
    img_erode = cv2.erode(img_dilate, kernel, iterations=1)

    # Find the contour
    _, cnts, hier = cv2.findContours(img_erode, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(cnts) == 0:
        print('no contours')
        return []

    # The hierarchy from cv2.findContours() is similar to a tree: each node has an access to the parent,
    # the first child, their previous and next nodes.
    # Using recursive search, find the uppermost contour in the hierarchy that satisfies the condition
    # The candidate contour must be rectangle (has 4 points) and should be larger than a threshold
    cnts_rect = []
    stack = [(0, hier[0][0])]
    while len(stack) > 0:
        i_cnt, h = stack.pop()
        i_next, i_prev, i_child, i_parent = h
        if i_next != -1:
            stack.append((i_next, hier[0][i_next]))

        cnt = cnts[i_cnt]
        size = cv2.contourArea(cnt)
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)

        if size >= size_thresh and len(approx) == 4:
            cnts_rect.append(approx)
            print(size)
        else:
            if i_child != -1:
                stack.append((i_child, hier[0][i_child]))

    return cnts_rect


def detect_frame(img, card_pool=None, hash_size=32, size_thresh=70000, out_path=None, display=True, debug=False):
    img_result = img.copy()
    det_cards = []

    # Detect contours of cards in the image
    cnts = find_card(img_result, size_thresh=size_thresh)
    for i in range(len(cnts)):
        cnt = cnts[i]

        # For the region of the image covered by the contour, transform them into a rectangular image
        pts = np.float32([p[0] for p in cnt])
        img_warp = four_point_transform(img, pts)

        # Okay, who is it?
        card_id, quality = cm.MatchCardImg(img_warp)
        data = cl.lookup(card_id)

        cv2.drawContours(img_result, [cnt], -1, (0, 255, 0), 2)
        cv2.putText(img_result, data['name'], (min(pts[0][0], pts[1][0]), min(pts[0][1], pts[1][1])),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    cv2.imshow('found', img_result)



path_db_root = join(dirname(__file__), 'scryfall-data')
path_hash_db = join(path_db_root, 'hash_db.pickle')
path_card_db = join(path_db_root, 'scryfall-default-cards.pickle')

cm = CardMatcher(path_hash_db)
cl = CardLookup(path_card_db)

cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture('/Users/adam/repos/mtg-inventory/mtg-inventory/testdata/garage_video2.mov')
if not cap.isOpened():
    cap.open()

while True:
    ret, frame = cap.read()

    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    detect_frame(frame)

cap.release
cv2.destroyAllWindows()
