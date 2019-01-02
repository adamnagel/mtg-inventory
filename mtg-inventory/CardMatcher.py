import json
import numpy as np
from os.path import join, dirname
from time import time
from build_hash_db import HashImg

path_db_root = '/Volumes/SSDshare/scryfall-data/'
path_image_db_root = join(path_db_root, 'img')
path_hash_db = join(path_db_root, 'hash_db.json')


# What do we need to do?
# Let's open the hash database.
# We need to turn it into numpy structures we can use the CUDA compute on.

# So let's make 2 data structures from the input.
# One is just all the IDs in order.
# The other is all the coefficients, as a 24-element vector.

class CardMatcher(object):
    def __init__(self, path_hash_db):
        with open(path_hash_db, encoding="utf8") as f:
            hash_db = json.load(f)

        # Parse Database
        l_coefficients = []
        l_ids = []
        set_lengths = set()
        d_ids = dict()
        for entry in hash_db:
            # coeffs = self.DataDictToVector(entry['data'])
            coeffs = []

            for k in entry['data'].keys():
                for k2, v2 in entry['data'][k].items():
                    coeffs.extend(v2)

            l_ids.append(entry['_id'])
            l_coefficients.append(coeffs)
            set_lengths.add(len(coeffs))

            d_ids[entry['_id']] = {
                '_filepath': entry['_file']
            }

        print('lengths: {}'.format(set_lengths))
        np_coefficients = np.array(l_coefficients)
        print('shape np_coefficients: {}'.format(np_coefficients.shape))

        self.np_coefficients = np_coefficients
        self.d_ids = d_ids
        self.l_ids = l_ids

    @staticmethod
    def DataDictToVector(d):
        coeffs = []

        for k in d.keys():
            for k2, v2 in d[k].items():
                coeffs.extend(v2)

        return coeffs

    def MatchCardCoeffs(self, np_coeffs):
        print('start comparison')

        start = time()
        np_sums = np.sum((np_coeffs - self.np_coefficients) ** 2, axis=1)
        end = time()

        print(np_sums)
        print('took {:.4g}ms'.format((end - start) * 1000))

        idx = np.argmin(np_sums)
        print('best match: {} for {}'.format(np_sums[idx], self.d_ids[self.l_ids[idx]]))
        # print(np_coefficients[idx])
        # print(np_testimage)

    def MatchCardImg(self, path_card):
        hash_testimage = self.DataDictToVector(HashImg(path_card))
        np_testimage = np.array(hash_testimage)

        self.MatchCardCoeffs(np_testimage)


cm = CardMatcher(path_hash_db)

path_testimage = join(dirname(__file__), 'testdata', 'feast_of_dreams_upright.jpg')
cm.MatchCardImg(path_testimage)
