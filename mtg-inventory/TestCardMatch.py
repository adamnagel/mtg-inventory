import unittest
from CardMatcher import CardMatcher
from os.path import join, dirname

path_db_root = 'C:\\SSDshare\\scryfall-data'
path_hash_db = join(path_db_root, 'hash_db.pickle')


class TestCardMatcher(unittest.TestCase):
    def setUp(self):
        self.cm = CardMatcher(path_hash_db)

    def test_FeastOfDreams_Ideal(self):
        path_testimage = join(dirname(__file__), 'testdata', 'jou-69-feast-of-dreams.jpg')
        id, _ = self.cm.MatchCardFile(path_testimage)
        self.assertEqual(id, 'de07e21e-c12a-47a6-ad2c-ef6fed343407')

    def test_FeastOfDreams_Crop(self):
        path_testimage = join(dirname(__file__), 'testdata', 'feast_of_dreams crop.jpg')
        id, _ = self.cm.MatchCardFile(path_testimage)
        self.assertEqual(id, 'de07e21e-c12a-47a6-ad2c-ef6fed343407')

    def test_FeastOfDreams_Raw(self):
        path_testimage = join(dirname(__file__), 'testdata', 'feast_of_dreams.jpg')
        id, _ = self.cm.MatchCardFile(path_testimage)
        self.assertEqual(id, 'de07e21e-c12a-47a6-ad2c-ef6fed343407')

    def test_FeastOfDreams_Poor(self):
        path_testimage = join(dirname(__file__), 'testdata', 'feast_of_dreams_poor.jpg')
        id, _ = self.cm.MatchCardFile(path_testimage)
        self.assertEqual(id, 'de07e21e-c12a-47a6-ad2c-ef6fed343407')
