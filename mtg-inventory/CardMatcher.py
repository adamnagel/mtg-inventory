import json
import numpy as np
from os.path import join, dirname
from time import time
from BuildHashDb import HashImgFile, HashImg
import pickle

with open('config.json') as f:
    config = json.load(f)
path_db_root = config['path_db_root']

path_hash_db = join(path_db_root, 'hash_db.pickle')


# What do we need to do?
# Let's open the hash database.
# We need to turn it into numpy structures we can use the CUDA compute on.

# So let's make 2 data structures from the input.
# One is just all the IDs in order.
# The other is all the coefficients, as a 24-element vector.

class CardMatcher(object):
    def __init__(self, path_hash_db=path_hash_db):
        start = time()

        with open(path_hash_db, 'rb') as f:
            hash_db = pickle.load(f)

        duration = time() - start
        print('loaded db in {:.4g}s'.format(duration))
        self.hash_db = hash_db

    def MatchCardFile(self, path_card):
        hash_card = HashImgFile(path_card)

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

        return best_id, best_val

    def MatchCardImg(self, img_card, matches=1):
        hash_card = HashImg(img_card)

        # This is a set of tuples, with (id, quality)
        best_matches = MatchSet(max_length=matches)

        # best_val = None
        # best_id = None
        for k, v in self.hash_db.items():
            match = hash_card - v['data']

            best_matches.tryAdd(k, match, v['_file'])

        bm = best_matches.getSet()

        if matches == 1:
            bm0 = bm[0]
            return bm0[0], bm0[1]

        return bm


class MatchSet:
    def __init__(self, max_length=10):
        self.data = list()
        self.max_length = max_length
        self.length = 0
        self.worst_quality = 1e12

    def tryAdd(self, id, quality, file):
        # If quality isn't better, we don't care.
        if quality > self.worst_quality:
            return

        if self.length == 0:
            self.data = [(id, quality, file)]
            self.length = 1
            return

        # In this case, we need to insert into the right location.
        target_idx = -1
        for idx, match in enumerate(self.data):
            if quality < match[1]:
                target_idx = idx
                break

        self.data.insert(target_idx, (id, quality, file))

        # Remove final value is we're over length
        if len(self.data) > self.max_length:
            self.data.pop(-1)

        self.worst_quality = self.data[-1][1]

    def getSet(self):
        return self.data
