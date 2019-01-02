import unittest
from os.path import join, dirname
from HandleFrame import HandleFrame
from CardLookup import CardLookup

path_db_root = 'C:\\SSDshare\\scryfall-data'
path_hash_db = join(path_db_root, 'hash_db.pickle')
path_raw_captures = join(dirname(__file__), 'testdata', 'raw_captures')


class TestHandleFrameMatcher(unittest.TestCase):
    def setUp(self):
        self.cl = CardLookup()
        self.hf = HandleFrame()

    def test_StabWound(self):
        path_testimage = join(path_raw_captures, 'StabWound.jpg')
        best_id, best_quality = self.hf.handle_frame_img(path_testimage)

        print('quality {}'.format(best_quality))

        name = self.cl.lookup(best_id)['name']
        self.assertEqual(name, 'Stab Wound')

    def test_SlateStreetRuffian(self):
        path_testimage = join(path_raw_captures, 'SlateStreetRuffian.jpg')
        best_id, best_quality = self.hf.handle_frame_img(path_testimage)

        print('quality {}'.format(best_quality))

        name = self.cl.lookup(best_id)['name']
        self.assertEqual(name, 'Slate Street Ruffian')

    def test_Forest(self):
        path_testimage = join(path_raw_captures, 'Forest.jpg')
        best_id, best_quality = self.hf.handle_frame_img(path_testimage)

        print('quality {}'.format(best_quality))

        name = self.cl.lookup(best_id)['name']
        self.assertEqual(name, 'Forest')
        self.assertEqual(best_id, 'ee05a26d-b872-4d49-9860-2fd982b3662f')

    def test_Forest2(self):
        path_testimage = join(path_raw_captures, 'Forest2.jpg')
        best_id, best_quality = self.hf.handle_frame_img(path_testimage)

        print('quality {}'.format(best_quality))

        name = self.cl.lookup(best_id)['name']
        self.assertEqual(name, 'Forest')

    def test_Forest3(self):
        path_testimage = join(path_raw_captures, 'Forest3.jpg')
        best_id, best_quality = self.hf.handle_frame_img(path_testimage)

        print('quality {}'.format(best_quality))

        name = self.cl.lookup(best_id)['name']
        self.assertEqual(name, 'Forest')

    def test_Forest4(self):
        path_testimage = join(path_raw_captures, 'Forest4.jpg')
        best_id, best_quality = self.hf.handle_frame_img(path_testimage)

        print('quality {}'.format(best_quality))

        name = self.cl.lookup(best_id)['name']
        self.assertEqual(name, 'Forest')

    def test_GatecreeperVine(self):
        path_testimage = join(path_raw_captures, 'GatecreeperVine.jpg')
        best_id, best_quality = self.hf.handle_frame_img(path_testimage)

        print('quality {}'.format(best_quality))

        name = self.cl.lookup(best_id)['name']
        self.assertEqual(name, 'Gatecreeper Vine')

    def test_RiverBoa(self):
        path_testimage = join(path_raw_captures, 'RiverBoa.jpg')
        best_id, best_quality = self.hf.handle_frame_img(path_testimage)

        print('quality {}'.format(best_quality))

        name = self.cl.lookup(best_id)['name']
        self.assertEqual(name, 'River Boa')
        self.assertEqual(best_id, 'edfbf056-c3b7-40e9-8e2b-333585978ac9')

    def test_HypnoticCloud(self):
        path_testimage = join(path_raw_captures, 'HypnoticCloud.jpg')
        best_id, best_quality = self.hf.handle_frame_img(path_testimage)

        print('quality {}'.format(best_quality))

        name = self.cl.lookup(best_id)['name']
        self.assertEqual(name, 'Hypnotic Cloud')
        self.assertEqual(best_id, '62e55607-4c1f-46ab-aae7-391b65a125c4')

    def test_RoguesPassage(self):
        path_testimage = join(path_raw_captures, 'Rogue\'sPassage.jpg')
        best_id, best_quality = self.hf.handle_frame_img(path_testimage)

        print('quality {}'.format(best_quality))

        name = self.cl.lookup(best_id)['name']
        self.assertEqual(name, 'Rogue\'s Passage')

    def test_ConsumeStrength(self):
        path_testimage = join(path_raw_captures, 'ConsumeStrength.jpg')
        best_id, best_quality = self.hf.handle_frame_img(path_testimage)

        print('quality {}'.format(best_quality))

        name = self.cl.lookup(best_id)['name']
        self.assertEqual(name, 'Consume Strength')
