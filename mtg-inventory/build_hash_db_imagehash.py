# magick identify -quiet -verbose -moments -alpha off mtg-inventory/testdata/feast_of_dreams.jpg

from os.path import dirname, join, exists
import json
from subprocess import check_output
import re
from os import walk
from multiprocessing import Pool
from copy import copy
import imagehash as ih
import cv2
from PIL import Image
import pickle

re_phash_start = '\s*Channel perceptual hash: sRGB'
rec_phash_start = re.compile(re_phash_start)

re_channel = '\s*Channel \d:'
rec_channel = re.compile(re_channel)

re_ph_pair = '\s*PH\d: .*, .*'
rec_ph_pair = re.compile(re_ph_pair)

re_ph_end = '\sRendering intent: Perceptual'
rec_ph_end = re.compile(re_ph_end)

# path_db_root = 'C:\\SSDshare\\scryfall-data'
# path_db_root = '/Volumes/SSDshare/scryfall-data/'
path_db_root = '/Users/adam/repos/mtg-inventory/mtg-inventory/scryfall-data'
path_image_db_root = join(path_db_root, 'img')
path_hash_db = join(path_db_root, 'hash_db.pickle')


def HashImg(path_img):
    card_img = cv2.imread(path_img)

    img_card = Image.fromarray(card_img)

    card_hash = ih.phash(img_card, hash_size=32)
    data = card_hash
    return data


def HashImgWrap(item):
    rtn = copy(item)
    rtn['data'] = HashImg(item['_abspath'])
    return rtn


if __name__ == '__main__':
    if exists(path_hash_db):
        with open(path_hash_db, 'rb') as f:
            hash_db = pickle.load(f)
    else:
        hash_db = dict()

    # What do we want to do?
    # We want to open the existing Hash DB and index the IDs.
    # Then we want to skip any images we've already indexed.

    ids_completed = hash_db.keys()

    max = 1000
    files_db = []
    skipped = 0

    for root, dirs, files in walk(path_image_db_root):
        if max == 0:
            break

        for name in files:
            id = name.replace('.jpg', '')
            if id in ids_completed:
                skipped += 1
                continue

            if max == 0:
                break

            max -= 1

            abspath = join(root, name)
            relpath = abspath.replace(path_image_db_root, '')
            files_db.append({
                '_id': id,
                '_file': relpath,
                '_abspath': abspath
            })

    print('Skipped {} already indexed'.format(skipped))
    print('Indexing {} card images'.format(len(files_db)))

    with Pool() as p:
        r = p.map(HashImgWrap, files_db)

    new_db = {i['_id']: i for i in r}
    combined_db = {**hash_db, **new_db}

    with open(path_hash_db, 'wb') as handle:
        pickle.dump(combined_db, handle)
