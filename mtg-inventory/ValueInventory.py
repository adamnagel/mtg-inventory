import json
import requests
from time import sleep

api = 'https://api.scryfall.com/cards/{}'

with open('inventory_1546659474.956449', 'r') as f:
    inventory = json.load(f)

d_ids = {card['id']: card for card in inventory}

for id in d_ids.keys():
    r_raw = requests.get(api.format(id))
    r = r_raw.json()

    name = d_ids[id]['name']
    usd = None
    if 'usd' in r:
        usd = r['usd']

    print('{}: {}'.format(name, usd))

    sleep(0.1)
