from PIL import Image
from multiprocessing import Pool

from cv2 import imdecode, imread, IMREAD_UNCHANGED
from imagehash import phash
import numpy as np
import pickle
from copy import copy
from os import walk, stat
from os.path import join, exists

path_db_root = 'C:\\SSDshare\\scryfall-data'
# path_db_root = '/Volumes/SSDshare/scryfall-data/'
# path_db_root = '/Users/adam/repos/mtg-inventory/mtg-inventory/scryfall-data'
path_image_db_root = join(path_db_root, 'img')
path_hash_db = join(path_db_root, 'hash_db.pickle')


def HashImgFile(path_img):
    # This roundabout method is needed to handle Unicode paths.
    stream = open(path_img, 'rb')
    bytes = bytearray(stream.read())
    numpyarray = np.asarray(bytes, dtype=np.uint8)
    card_img = imdecode(numpyarray, IMREAD_UNCHANGED)

    # This simple method doesn't support Unicode paths
    # card_img = imread(path_img)

    hash_card = HashImg(card_img)

    return hash_card


def HashImg(card_img):
    img_card = Image.fromarray(card_img)
    hash_card = phash(img_card, hash_size=32)

    return hash_card


def HashImgWrap(item):
    rtn = copy(item)
    path_img = item['_abspath']

    try:
        hash_card = HashImgFile(path_img)
        rtn['data'] = hash_card

    except:
        print('failed on {}'.format(item['_file']))

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

    files_db = []
    skipped = 0

    for root, dirs, files in walk(path_image_db_root):
        for name in files:
            id = name.replace('.jpg', '')
            if id in ids_completed:
                skipped += 1
                continue

            abspath = join(root, name)
            relpath = abspath.replace(path_image_db_root, '')

            # If less than 50k, ignore
            if stat(abspath).st_size < 20 * 1000:
                print('ignoring {} due to size'.format(relpath))
                continue

            files_db.append({
                '_id': id,
                '_file': relpath,
                '_abspath': abspath
            })

    print('Skipped {} already indexed'.format(skipped))
    print('Indexing {} card images'.format(len(files_db)))

    with Pool() as p:
        r = p.map(HashImgWrap, files_db)

    for i in r:
        hash_db[i['_id']] = i

    with open(path_hash_db, 'wb') as handle:
        pickle.dump(hash_db, handle)
