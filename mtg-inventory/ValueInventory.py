import json
import requests
from time import sleep
from os.path import join

api = 'https://api.scryfall.com/cards/{}'


def CardValue(id):
    r_raw = requests.get(api.format(id))
    r = r_raw.json()

    usd = None
    if 'usd' in r:
        usd = r['usd']
    return usd


if __name__ == '__main__':
    with open(join('..', 'library', 'Baseball Binder - Pages 1 to 4.json'), 'r') as f:
        inventory = json.load(f)

    d_ids = {card['id']: card for card in inventory}

    for id in d_ids.keys():
        name = d_ids[id]['name']
        d_ids[id]['usd'] = CardValue(id)

        # print('{}: {}'.format(name, usd))

        sleep(0.1)

    for id in sorted(d_ids, key=lambda id: float(d_ids[id]['usd']), reverse=True):
        print('{}: {}'.format(d_ids[id]['usd'], d_ids[id]['name']))
