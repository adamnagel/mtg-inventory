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

        start = time()
        with open(path_hash_db, encoding="utf8") as f:
            hash_db = json.load(f)
        duration = time() - start
        print('loaded db in {:.4g}ms'.format(duration * 1000))
        # self.hash_db = hash_db

        # Parse Database
        l_coefficients = []
        l_ids = []
        set_lengths = set()
        d_ids = dict()

        start = time()
        for entry in hash_db:
            if len(entry['data'].keys()) != 3:
                print('wrong coeffs for {}'.format(entry['_file']))
                continue

            coeffs = self.DataDictToVector(entry['data'])

            len_coeffs = len(coeffs)
            # if len_coeffs != 35:
            #     print('wrong length ({}) for {}'.format(len_coeffs, entry['_file']))
            #     continue

            l_ids.append(entry['_id'])
            l_coefficients.append(coeffs)
            set_lengths.add(len_coeffs)

            d_ids[entry['_id']] = {
                '_file': entry['_file']
            }

        print('lengths: {}'.format(set_lengths))
        np_coefficients = np.array(l_coefficients)
        print('shape np_coefficients: {}'.format(np_coefficients.shape))

        duration = time() - start
        print('transformed db in {:.4g}ms'.format(duration * 1000))

        self.np_coefficients = np_coefficients
        self.d_ids = d_ids
        self.l_ids = l_ids

    @staticmethod
    def DataDictToVector(d):
        coeffs = []

        # Channel 0: Red, Hue
        # Channel 1: Green, Chroma
        # Channel 2: Blue, Luma

        # style = 'Luma'
        style = 'NoHue'

        if style is 'NoHue':
            for k, v in d['Channel 0'].items():
                coeffs.append(v[0])
            for k, v in d['Channel 1'].items():
                coeffs.extend(v)
            for k, v in d['Channel 2'].items():
                coeffs.extend(v)

        elif style is 'Luma':
            for k, v in d['Channel 2'].items():
                coeffs.append(v[1])

        elif style is 'Full':
            for k in d.keys():
                for k2, v2 in d[k].items():
                    coeffs.extend(v2)

        return coeffs

    def MatchCardCoeffs(self, np_card_coeffs):
        # print('start comparison')

        start = time()
        np_sums = np.sum((np_card_coeffs - self.np_coefficients) ** 2, axis=1)
        end = time()

        # print(np_sums)
        # print('took {:.4g}ms'.format((end - start) * 1000))

        idx = np.argmin(np_sums)
        print('best match: {} for {}'.format(np_sums[idx], self.d_ids[self.l_ids[idx]]))
        # print(np_coefficients[idx])
        # print(np_testimage)

        # What's the match with Feast of Dreams?
        ids_fod = set()
        for k, v in self.d_ids.items():
            if 'Feast' in v['_file'] and 'Dreams' in v['_file']:
                ids_fod.add(k)
        # print(ids_fod)

        for id_fod in ids_fod:
            idx_fod = self.l_ids.index(id_fod)
            np_fod_coeffs = self.np_coefficients[idx_fod]

            print(np.sum((np_card_coeffs - np_fod_coeffs) ** 2))

    def MatchCardImg(self, path_card):
        hash_testimage = self.DataDictToVector(HashImg(path_card))
        np_testimage = np.array(hash_testimage)

        self.MatchCardCoeffs(np_testimage)


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
