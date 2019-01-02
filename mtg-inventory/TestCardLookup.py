import unittest
from os.path import join, dirname
from CardLookup import CardLookup

path_db_root = 'C:\\SSDshare\\scryfall-data'
path_card_db = join(path_db_root, 'scryfall-default-cards.pickle')


class TestCardLookup(unittest.TestCase):
    def setUp(self):
        self.cl = CardLookup()

    def test_FeastOfDreams(self):
        data = self.cl.lookup('de07e21e-c12a-47a6-ad2c-ef6fed343407')
        self.assertEqual(data['name'], 'Feast of Dreams')
