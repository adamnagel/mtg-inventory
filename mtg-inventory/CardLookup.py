import pickle
from os.path import join, exists
import json

path_db_root = 'C:\\SSDshare\\scryfall-data'
path_card_db = join(path_db_root, 'scryfall-default-cards.pickle')
path_card_db_json = join(path_db_root, 'scryfall-default-cards.json')


class CardLookup(object):
    def __init__(self, card_db=path_card_db):
        if not exists(path_card_db):
            with open(path_card_db_json, 'r', encoding='utf8') as f:
                card_db_raw = json.load(f)

            card_db = {i['id']: i for i in card_db_raw}

            with open(path_card_db, 'wb') as f:
                pickle.dump(card_db, f)

        else:
            with open(path_card_db, 'rb') as f:
                card_db = pickle.load(f)

        self.card_db = card_db

    def lookup(self, id):
        return self.card_db[id]
