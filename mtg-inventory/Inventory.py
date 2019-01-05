from VideoStream import detect_frame
from os.path import join, dirname
from CardMatcher import CardMatcher
from CardLookup import CardLookup
import cv2
import numpy as np
from BuildHashDb import LoadImg
from time import time
import json

path_db_root = join(dirname(__file__), 'scryfall-data')
path_hash_db = join(path_db_root, 'hash_db.pickle')
path_card_db = join(path_db_root, 'scryfall-default-cards.pickle')
path_image_db_root = join(path_db_root, 'img')


def detect_cards(img, size_thresh=16000):
    det_card_images = detect_frame(img, size_thresh=size_thresh)

    for card in det_card_images:
        img_card = card[0]
        cnt_card = card[1]

        # Okay, who is it?
        matches = cm.MatchCardImg(img_card, matches=20)
        print(matches)

        data = cl.lookup(matches[0][0])
        print(data)

        #
        # pts = np.float32([p[0] for p in cnt_card])
        # cv2.drawContours(img_result, [cnt_card], -1, (0, 255, 0), 2)
        # cv2.putText(img_result, data['name'], (min(pts[0][0], pts[1][0]), min(pts[0][1], pts[1][1])),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # cv2.imshow('found', img_result)


cm = CardMatcher(path_hash_db)
cl = CardLookup(path_card_db)

# cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(join(path_db_root, '3_card_video.mp4'))
if not cap.isOpened():
    cap.open()

# States
SCAN = 0
SELECT = 1

# Constants
MAX_MATCHES = 10

# State variables
match_idx = 0
state = SCAN
img_card = None
inventory = list()

cv2.namedWindow('camera')
cv2.moveWindow('camera', 0, 0)

while True:
    # cv2.imshow('frame', frame)
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break

    if key & 0xFF == ord('d'):
        if state == SCAN:
            state = SELECT
            match_idx = 0

    elif key & 0xFF == ord('a'):
        if state == SCAN:
            state = SELECT
            match_idx = 0

    if state == SCAN:
        ret, frame = cap.read()
        if ret is None or frame is None:
            break

        det_card_images = detect_frame(frame, size_thresh=16000)

        if len(det_card_images) == 0:
            img_card = None
            continue

        card = det_card_images[0]
        img_card = card[0]
        cnt_card = card[1]

        cv2.imshow('camera', img_card)

    if state == SELECT:
        # If we have no card image currently captured, proceed.
        if img_card is None:
            state = SCAN
            continue

        matches = cm.MatchCardImg(img_card, matches=MAX_MATCHES)

        match = matches[match_idx]

        subpath_library_image = match[2][1:].replace('\\', '/')
        path_library_image = join(path_image_db_root, subpath_library_image)

        img_library = LoadImg(path_library_image)

        # Create a composite window image for this in 'camera'
        height_img_library, _, _ = img_library.shape
        height_img_card, _, _ = img_card.shape
        expand_by = height_img_library - height_img_card

        img_card_scaled = cv2.copyMakeBorder(img_card, 0, expand_by, 0, 0, cv2.INTER_NEAREST)

        img_composite = np.concatenate((img_card_scaled, img_library), axis=1)

        cv2.imshow('camera', img_composite)

        key = cv2.waitKey(0)
        if key & 0xFF == ord('d'):
            match_idx += 1
            if match_idx > 10:
                match_idx = 10

        elif key & 0xFF == ord('a'):
            match_idx -= 1
            if match_idx < 0:
                match_idx = 0

        elif key & 0xFF == ord('x'):
            # Cancel and go back to scanning
            state = SCAN

        elif key & 0xFF == ord(' '):
            # Select this card and go back to normal.
            data = cl.lookup(matches[0][0])
            print(data)
            inventory.append({
                'id': data['id'],
                'name': data['name']
            })
            state = SCAN

if len(inventory) > 0:
    with open('inventory_{}'.format(time()), 'w') as inv:
        json.dump(inventory, inv, indent=2)

cap.release
cv2.destroyAllWindows()
