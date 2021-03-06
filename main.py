import csv
import json
import os
from itertools import product

from dataPrep.db import dbSession
from dataPrep.features import Features
from whr.whole_history_rating import Base

if __name__ == "__main__":
    data = []
    if input('Download new play data?\n')[0].lower() == 'y':
        for y, w in product(range(2018, 2019), range(1, 16)):
            g = dbSession.query_games(year=y, week=w)
            p = [{**x, "week": w, "year": y} for x in dbSession.query_plays(year=y, week=w)]
            for i in p:
                for j in g:
                    if {i['defense'], i['offense']} == {j['home_team'], j['away_team']}:
                        i['away'], i['home'] = j['away_team'], j['home_team']
                        data.append(i)
                        break

        with open(os.path.join('data', 'plays.json'), 'w+') as outfile:
            json.dump(data, outfile)

    if input('Process and label plays?\n')[0].lower() == 'y':
        f = Features(file=os.path.join('data', 'plays.json'))
        f.label_successes()
        f.export_segmented_labeled_csv()

    if input('Merge with existing ratings?\n')[0].lower() == 'y':
        with open(os.path.join('data', 'ELO ratings.json'), 'w+') as infile:
            results = json.load(infile)
    else:
        results = {}

    # run the whole history rating for each feature

    whr = Base(config={"w2": 14})

    for file in [n for n in os.listdir('data') if n.endswith('.csv')]:
        with open(os.path.join('data', file), 'r') as infile:
            plays = [x for x in csv.reader(infile)]

        whr.load_plays(plays)
        whr.auto_iterate()
        for t in whr.get_ordered_ratings(current=True):
            for x in ('offense', 'defense'):
                team = t[0].split(' ')
                if team[-1] == x:
                    try:
                        results[' '.join(team[:-1])]['_'.join([x, file.__str__().split('.')[0]])] = t[1]
                    except KeyError:
                        results[' '.join(team[:-1])] = {'_'.join([x, file.__str__().split('.')[0]]): t[1]}

        with open(os.path.join('data', 'ELO ratings.json'), 'w+') as outfile:
            json.dump(results, outfile, indent=4, sort_keys=True)
