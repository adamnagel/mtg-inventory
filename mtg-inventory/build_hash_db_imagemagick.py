# magick identify -quiet -verbose -moments -alpha off mtg-inventory/testdata/feast_of_dreams.jpg

from os.path import dirname, join, exists
import json
from subprocess import check_output
import re
from os import walk
from multiprocessing import Pool
from copy import copy

re_phash_start = '\s*Channel perceptual hash: sRGB'
rec_phash_start = re.compile(re_phash_start)

re_channel = '\s*Channel \d:'
rec_channel = re.compile(re_channel)

re_ph_pair = '\s*PH\d: .*, .*'
rec_ph_pair = re.compile(re_ph_pair)

re_ph_end = '\sRendering intent: Perceptual'
rec_ph_end = re.compile(re_ph_end)

# path_db_root = 'C:\\SSDshare\\scryfall-data'
path_db_root = '/Volumes/SSDshare/scryfall-data/'
path_image_db_root = join(path_db_root, 'img')
path_hash_db = join(path_db_root, 'hash_db.json')


def HashImg(path_img):
    result = check_output([
        'magick',
        'identify',
        '-quiet',
        '-verbose',
        '-moments',
        '-alpha',
        'off',
        path_img
    ], text=True)

    data = {}
    active = False
    channel_dict = {}

    for line in result.split('\n'):
        if rec_phash_start.match(line):
            active = True
            continue

        if rec_ph_end.match(line):
            active = False

        if not active:
            continue

        if rec_channel.match(line):
            num_channel = re.search('(?<=Channel )[0-9]{1}', line).group(0)
            channel = 'Channel {}'.format(num_channel)

            data[channel] = {}
            channel_dict = data[channel]

        if rec_ph_pair.match(line):
            trimline = line.strip()
            ph_, nums = trimline.split(':')

            num1, num2 = nums.strip().split(',')

            channel_dict[ph_] = [float(num1), float(num2)]

    # return result
    # print (json.dumps(data, indent=2))
    return data


def HashImgWrap(item):
    rtn = copy(item)
    rtn['data'] = HashImg(item['_abspath'])
    return rtn


if __name__ == '__main__':
    if exists(path_hash_db):
        with open(path_hash_db, encoding="utf8") as f:
            hash_db = json.load(f)
    else:
        hash_db = dict()

    # What do we want to do?
    # We want to open the existing Hash DB and index the IDs.
    # Then we want to skip any images we've already indexed.

    ids_completed = []
    for i in hash_db:
        ids_completed.append(i['_id'])

    max = 1
    files_db = []
    skipped = 0

    for root, dirs, files in walk(path_image_db_root, topdown=False):
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

    combined_db = []
    combined_db.extend(hash_db)
    combined_db.extend(r)

    with open(path_hash_db, 'w', encoding="utf8") as f:
        json.dump(combined_db, f, indent=2, sort_keys=True)
