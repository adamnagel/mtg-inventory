import json
import numpy as np
from os.path import join, dirname
from time import time
from build_hash_db_imagehash import HashImg
import pickle

path_db_root = '/Volumes/SSDshare/scryfall-data/'
path_image_db_root = join(path_db_root, 'img')
path_hash_db = join(path_db_root, 'hash_db.pickle')


# What do we need to do?
# Let's open the hash database.
# We need to turn it into numpy structures we can use the CUDA compute on.

# So let's make 2 data structures from the input.
# One is just all the IDs in order.
# The other is all the coefficients, as a 24-element vector.

class CardMatcher(object):
    def __init__(self, path_hash_db):
        start = time()

        with open(path_hash_db, 'rb') as f:
            hash_db = pickle.load(f)

        duration = time() - start
        print('loaded db in {:.4g}s'.format(duration))
        self.hash_db = hash_db

    def MatchCardImg(self, path_card):
        hash_card = HashImg(path_card)

        start = time()
        best_val = None
        best_id = None
        for k, v in self.hash_db.items():
            match = hash_card - v['data']

            if not best_val:
                best_val = match
                best_id = k
            elif match < best_val:
                best_val = match
                best_id = k

        duration = time() - start
        print('{:.4g}ms'.format(duration))

        print(self.hash_db[best_id]['_file'])


cm = CardMatcher(path_hash_db)

path_testimage = join(dirname(__file__), 'testdata', 'feast_of_dreams.jpg')
cm.MatchCardImg(path_testimage)
path_testimage = join(dirname(__file__), 'testdata', 'feast_of_dreams copy.jpg')
cm.MatchCardImg(path_testimage)
path_testimage = join(dirname(__file__), 'testdata', 'feast_of_dreams_poor.jpg')
cm.MatchCardImg(path_testimage)
path_testimage = join(dirname(__file__), 'testdata', 'jou-69-feast-of-dreams.jpg')
cm.MatchCardImg(path_testimage)
path_testimage = join(dirname(__file__), 'testdata', 'feast_of_dreams crop.jpg')
cm.MatchCardImg(path_testimage)
path_testimage = join(dirname(__file__), 'testdata', 'jou-69-feast-of-dreams-480.jpg')
cm.MatchCardImg(path_testimage)
