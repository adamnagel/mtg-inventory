# magick identify -quiet -verbose -moments -alpha off mtg-inventory/testdata/feast_of_dreams.jpg

from os.path import dirname, join, exists
import json
from subprocess import call, check_output
import re

re_phash_start = '\s*Channel perceptual hash: sRGB'
rec_phash_start = re.compile(re_phash_start)

re_channel = '\s*Channel \d:'
rec_channel = re.compile(re_channel)

re_ph_pair = '\s*PH\d: .*, .*'
rec_ph_pair = re.compile(re_ph_pair)

re_ph_end = '\sRendering intent: Perceptual'
rec_ph_end = re.compile(re_ph_end)

path_image_db_root = join(dirname(__file__), 'scryfall-data', 'img')
path_hash_db = join(dirname(__file__), 'scryfall-data', 'hash_db.json')

if exists(path_hash_db):
    with open(path_hash_db) as f:
        hash_db = json.load(f)
else:
    hash_db = dict()


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
    ])

    ph = {}
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

            ph[channel] = {}
            channel_dict = ph[channel]

        if rec_ph_pair.match(line):
            # search = re.search('(?<=PH)[0-9]{1}: .*, .*', line)
            #
            # num_ph = search.group(0)
            # ph1 = search.group(1)
            # ph2 = search.group(2)

            trimline = line.strip()
            ph_, nums = trimline.split(':')

            num1, num2 = nums.strip().split(',')

            channel_dict[ph_] = [float(num1), float(num2)]

    # return result
    print (json.dumps(ph, indent=2))


data = HashImg(join(path_image_db_root, 'F', 'Forest', '3a11f9c9-267a-4913-97f7-78c372fe211e.jpg'))
print (data)
