import json
from os.path import join, dirname
from os import walk
from CardLookup import CardLookup

path_library = join(dirname(__file__), '..', 'library')
cl = CardLookup()

d_sets = {
    'dpa': '"Duels of the Planeswalkers"',
    'tddd': '"Duel Decks: Garruk vs. Liliana"',
    'dvd': '"Duel Decks: Divine vs. Demonic"',
    'tddm': '"Duel Decks: Jace vs. Vraska"',
    'rqs': '',
    'tm12': 'm12',
}


def translate(s):
    if s in d_sets:
        return d_sets[s]
    return s


for root, dirs, files in walk(path_library):
    for name in files:
        if not name.endswith('.json'):
            continue

        with open(join(root, name), encoding='utf8') as f:
            db = json.load(f)

            for card in db:
                card_data = cl.lookup(card['id'])
                # print(card)

                if card_data['set'] == 'rqs':
                    continue
                if 'proxy' in card:
                    continue

                print('"{name}",{set},1,{foil}'.format(name=card_data['name'],
                                                       set=translate(card_data['set']),
                                                       foil='foil' in card and card['foil']))
