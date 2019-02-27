import csv
import json
import os


class Features(object):
    __slots__ = ['plays', 'labeled', 'file']
    labeled_fields = ['home', 'away', 'clock', 'defense', 'offense', 'distance', 'down', "drive_id", 'id', 'period',
                      'play_type',
                      'week', 'yard_line', 'yards_gained', 'year']

    def __init__(self, file):
        self.file = file
        with open(file, 'r') as infile:
            self.plays = json.load(infile)
            self.labeled = []
            self.label_successes()

    def label_successes(self):
        for play in self.plays:
            temp = {x: play[x] for x in Features.labeled_fields}
            passing_down = False
            if play['down'] == 1:
                if play['yards_gained'] >= 0.5 * play['distance']:
                    temp['offensive_success'] = 1
                    temp['defensive_success'] = 0
                    temp['standard_down_offensive_rush_success'] = 1
                    temp['standard_down_defensive_rush_success'] = 0

                    if play['play_type'] == 'Rush':
                        temp['first_down_offensive_rush_success'] = 1
                        temp['first_down_defensive_rush_success'] = 0
                    elif play['play_type'] == 'Pass':
                        temp['first_down_offensive_pass_success'] = 1
                        temp['first_down_defensive_pass_success'] = 0
                else:
                    temp['offensive_success'] = 0
                    temp['defensive_success'] = 1
                    temp['standard_down_offensive_rush_success'] = 0
                    temp['standard_down_defensive_rush_success'] = 1
                    if play['play_type'] == 'Rush':
                        temp['first_down_offensive_rush_success'] = 0
                        temp['first_down_defensive_rush_success'] = 1
                    elif play['play_type'] == 'Pass':
                        temp['first_down_offensive_pass_success'] = 0
                        temp['first_down_defensive_pass_success'] = 1
            elif play['down'] == 2:
                if play['distance'] >= 8:
                    passing_down = True

                if play['yards_gained'] >= 0.7 * play['distance']:
                    temp['offensive_success'] = 1
                    temp['defensive_success'] = 0
                    if passing_down:
                        temp['passing_down_offensive_rush_success'] = 1
                        temp['passing_down_defensive_rush_success'] = 0
                    else:
                        temp['standard_down_offensive_rush_success'] = 1
                        temp['standard_down_defensive_rush_success'] = 0

                    if play['play_type'] == 'Rush':
                        temp['second_down_offensive_rush_success'] = 1
                        temp['second_down_defensive_rush_success'] = 0
                    elif play['play_type'] == 'Pass':
                        temp['second_down_offensive_pass_success'] = 1
                        temp['second_down_defensive_pass_success'] = 0
                else:
                    temp['offensive_success'] = 0
                    temp['defensive_success'] = 1
                    if passing_down:
                        temp['passing_down_offensive_rush_success'] = 0
                        temp['passing_down_defensive_rush_success'] = 1
                    else:
                        temp['standard_down_offensive_rush_success'] = 0
                        temp['standard_down_defensive_rush_success'] = 1

                    if play['play_type'] == 'Rush':
                        temp['second_down_offensive_rush_success'] = 0
                        temp['second_down_defensive_rush_success'] = 1
                    elif play['play_type'] == 'Pass':
                        temp['second_down_offensive_pass_success'] = 0
                        temp['second_down_defensive_pass_success'] = 1
            elif play['down'] == 3:
                if play['distance'] >= 5:
                    passing_down = True

                if play['yards_gained'] >= play['distance'] or play['play_type'].lower() == 'punt' or play[
                    'play_type'].lower() == 'field goal good':
                    temp['offensive_success'] = 1
                    temp['defensive_success'] = 0
                    if passing_down:
                        temp['passing_down_offensive_rush_success'] = 1
                        temp['passing_down_defensive_rush_success'] = 0
                    else:
                        temp['standard_down_offensive_rush_success'] = 1
                        temp['standard_down_defensive_rush_success'] = 0

                    if play['play_type'] == 'Rush':
                        temp['third_down_offensive_rush_success'] = 1
                        temp['third_down_defensive_rush_success'] = 0
                    elif play['play_type'] == 'Pass':
                        temp['third_down_offensive_pass_success'] = 1
                        temp['third_down_defensive_pass_success'] = 0
                else:
                    temp['offensive_success'] = 0
                    temp['defensive_success'] = 1
                    if passing_down:
                        temp['passing_down_offensive_rush_success'] = 0
                        temp['passing_down_defensive_rush_success'] = 1
                    else:
                        temp['standard_down_offensive_rush_success'] = 0
                        temp['standard_down_defensive_rush_success'] = 1

                    if play['play_type'] == 'Rush':
                        temp['third_down_offensive_rush_success'] = 0
                        temp['third_down_defensive_rush_success'] = 1
                    elif play['play_type'] == 'Pass':
                        temp['third_down_offensive_pass_success'] = 0
                        temp['third_down_defensive_pass_success'] = 1
            elif play['down'] == 4:
                if play['distance'] >= 5:
                    passing_down = True

                if play['yards_gained'] >= play['distance'] or play['play_type'].lower() == 'punt' or play[
                    'play_type'].lower() == 'field goal good':
                    temp['offensive_success'] = 1
                    temp['defensive_success'] = 0
                    if passing_down:
                        temp['passing_down_offensive_rush_success'] = 1
                        temp['passing_down_defensive_rush_success'] = 0
                    else:
                        temp['standard_down_offensive_rush_success'] = 1
                        temp['standard_down_defensive_rush_success'] = 0

                    if play['play_type'] == 'Rush':
                        temp['fourth_down_offensive_rush_success'] = 1
                        temp['fourth_down_defensive_rush_success'] = 0
                    elif play['play_type'] == 'Pass':
                        temp['fourth_down_offensive_pass_success'] = 1
                        temp['fourth_down_defensive_pass_success'] = 0
                else:
                    temp['offensive_success'] = 0
                    temp['defensive_success'] = 1
                    if passing_down:
                        temp['passing_down_offensive_rush_success'] = 0
                        temp['passing_down_defensive_rush_success'] = 1
                    else:
                        temp['standard_down_offensive_rush_success'] = 0
                        temp['standard_down_defensive_rush_success'] = 1

                    if play['play_type'] == 'Rush':
                        temp['fourth_down_offensive_rush_success'] = 0
                        temp['fourth_down_defensive_rush_success'] = 1
                    elif play['play_type'] == 'Pass':
                        temp['fourth_down_offensive_pass_success'] = 0
                        temp['fourth_down_defensive_pass_success'] = 1
            else:
                temp['offensive_success'] = -1
                temp['defensive_success'] = -1
            self.labeled.append(temp)

    def export_labeled_json(self, file=None):
        if not file:
            if file == self.file or not file:
                prompt = input('Overwrite existing file?')
                if len(prompt) == 1 and prompt.lower()[0] == 'y':
                    file = 'labeled.json'
                else:
                    file = input('New filename?')
                    if not file.endswith('.json'):
                        file += '.json'
        with open(file, 'w+') as outfile:
            json.dump(self.labeled, outfile, indent=4, sort_keys=True)

    def export_segmented_labeled_csv(self):
        categories = ('offensive_success',
                      'standard_down_offensive_rush_success',
                      'first_down_offensive_rush_success',
                      'first_down_offensive_pass_success',
                      'second_down_offensive_rush_success',
                      'second_down_offensive_pass_success',
                      'passing_down_offensive_rush_success',
                      'third_down_offensive_rush_success',
                      'third_down_offensive_pass_success',
                      'passing_down_offensive_pass_success',
                      'fourth_down_offensive_rush_success',
                      'fourth_down_offensive_pass_success',
                      )
        out = []

        for c in categories:
            cat = c.replace("_offensive", "")
            for p in self.labeled:
                if c in p.keys():
                    row = []
                    if p['home'] == p['offense']:
                        row.extend([p['home'] + ' offense', p['away'] + ' defense'])
                        if p[c] == 1:
                            row.extend(['H', p['week']])
                        else:
                            row.extend(['A', p['week']])
                    else:
                        row.extend([p['home'] + ' defense', p['away'] + ' offense'])
                        if p[c] == 1:
                            row.extend(['A', p['week']])
                        else:
                            row.extend(['H', p['week']])

                    out.append(row)
            with open(os.path.join('data', '{}.csv'.format(cat)), 'w+', newline='') as outfile:
                csvr = csv.writer(outfile)
                csvr.writerows(out)
