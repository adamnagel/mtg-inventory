from VideoStream import detect_frame
from os.path import join, dirname
from CardMatcher import CardMatcher
from CardLookup import CardLookup
import cv2
import numpy as np
from BuildHashDb import LoadImg
from time import time
import json
from ValueInventory import CardValue

with open(join(dirname(__file__), 'config.json')) as f:
    config = json.load(f)
path_db_root = config['path_db_root']

path_hash_db = join(path_db_root, 'hash_db.pickle')
path_card_db = join(path_db_root, 'scryfall-default-cards.pickle')
path_image_db_root = join(path_db_root, 'img')

cm = CardMatcher(path_hash_db)
cl = CardLookup(path_card_db)

cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture(join(path_db_root, '3_card_video.mp4'))
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
foil = False
proxy = False

cv2.namedWindow('camera')
cv2.moveWindow('camera', 80, 0)

while True:
    # cv2.imshow('frame', frame)
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break

    if key & 0xFF == ord('d') or key & 0xFF == ord('a') or key & 0xFF == ord(' '):
        if state == SCAN:
            state = SELECT
            match_idx = 0
            foil = False
            proxy = False

    if state == SCAN:
        ret, frame = cap.read()
        if ret is None or frame is None:
            break

        det_card_images = detect_frame(frame, size_thresh=16000)

        if len(det_card_images) == 0:
            img_card = None
            continue

        card = det_card_images[0]
        img_card_raw = card[0]
        cnt_card = card[1]

        img_card = cv2.resize(img_card_raw, (0, 0), fx=2.0, fy=2.0)

        cv2.imshow('camera', img_card)

    if state == SELECT:
        # If we have no card image currently captured, proceed.
        if img_card is None:
            state = SCAN
            continue

        matches = cm.MatchCardImg(img_card, matches=MAX_MATCHES)

        match = matches[match_idx]
        name = cl.lookup(match[0])['name']

        subpath_library_image = match[2][1:].replace('\\', '/')
        path_library_image = join(path_image_db_root, subpath_library_image)

        img_library = LoadImg(path_library_image)

        ### Create a composite window image for this in 'camera'
        height_img_library, _, _ = img_library.shape
        height_img_card, _, _ = img_card.shape
        expand_by = height_img_library - height_img_card

        img_card_scaled = cv2.copyMakeBorder(img_card, 0, expand_by, 0, 0, cv2.INTER_NEAREST)
        img_composite = np.concatenate((img_card_scaled, img_library), axis=1)

        # Now label the card beneath
        img_composite_border = cv2.copyMakeBorder(img_composite, 0, 200, 0, 0, cv2.INTER_NEAREST)
        height_screen, _, _ = img_composite_border.shape

        # name
        cv2.putText(img_composite_border,
                    name,
                    (50, height_screen - 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    2,
                    (255, 255, 255, 255),
                    2,
                    cv2.LINE_AA)
        # price
        cv2.putText(img_composite_border,
                    '${}'.format(CardValue(match[0])),
                    (50, height_screen - 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    2,
                    (255, 255, 255, 255),
                    2,
                    cv2.LINE_AA)

        if foil:
            cv2.putText(img_composite_border,
                        'FOIL',
                        (50, height_screen - 170),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        2,
                        (255, 255, 255, 255),
                        2,
                        cv2.LINE_AA)

        if proxy:
            cv2.putText(img_composite_border,
                        'PROXY',
                        (250, height_screen - 170),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        2,
                        (255, 255, 255, 255),
                        2,
                        cv2.LINE_AA)

        cv2.imshow('camera', img_composite_border)

        key = cv2.waitKey(0)
        if key & 0xFF == ord('d'):
            match_idx += 1
            if match_idx >= MAX_MATCHES:
                match_idx = MAX_MATCHES - 1

        elif key & 0xFF == ord('a'):
            match_idx -= 1
            if match_idx < 0:
                match_idx = 0

        elif key & 0xFF == ord('f'):
            foil = not foil

        elif key & 0xFF == ord('g'):
            proxy = not proxy

        elif key & 0xFF == ord('x') or key & 0xFF == ord('s'):
            # Cancel and go back to scanning
            state = SCAN

        elif key & 0xFF == ord(' '):
            # Select this card and go back to normal.
            data = cl.lookup(match[0])
            entry = {
                'id': data['id'],
                'name': data['name']
            }

            if foil:
                entry['foil'] = True
                print('(foil) {}'.format(data['name']))
            elif proxy:
                entry['proxy'] = True
                print('[proxy] {}'.format(data['name']))
            else:
                print(data['name'])

            inventory.append(entry)
            state = SCAN

if len(inventory) > 0:
    path_inventory = join(dirname(__file__), '..', 'library', 'inventory_{}.json'.format(time()))
    with open(path_inventory, 'w') as inv:
        json.dump(inventory, inv, indent=2)

cap.release
cv2.destroyAllWindows()
