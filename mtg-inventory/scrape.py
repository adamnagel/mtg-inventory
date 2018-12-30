import json
from os.path import join, dirname, exists
from os import makedirs
from time import sleep
import requests

path_db_root = join(dirname(__file__), 'scryfall-data')
path_db_json = join(path_db_root, 'scryfall-default-cards.json')
path_db_img = join(path_db_root, 'img')

with open('scryfall-data/scryfall-default-cards.json') as f:
    db = json.load(f)
print ('DB loaded')
print ('{} records'.format(len(db)))

index = {}
limit = 200

for card in db:
    if limit == 0:
        break
    limit -= 1

    name = card['name']
    id = card['id']
    url_border_crop_img = card['image_uris']['border_crop']
    print (url_border_crop_img)

    path_img_dir = join(path_db_img, name[0], name)
    if not exists(path_img_dir):
        makedirs(path_img_dir)
    path_img = join(path_img_dir, id + '.jpg')

    if not exists(path_img):
        r = requests.get(url_border_crop_img, allow_redirects=True)
        open(path_img, 'wb').write(r.content)

        sleep(0.1)

print ('done')
