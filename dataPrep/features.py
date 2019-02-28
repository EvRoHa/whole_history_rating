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

            if play['play_type'] == 'Rush':
                if play['yards_gained'] <= 0:
                    temp['run_stuff'] = 0
                else:
                    temp['run_stuff'] = 1

            if play['yards_gained'] >= 4:

                temp['opportunity'] = 1

                if play['play_type'] == 'Rush':

                    if play['yards_gained'] >= 12:

                        temp['explosive_rush'] = 1

                    else:

                        temp['explosive_rush'] = 0

                elif play['play_type'].startswith('Pass') or play['play_type'] == 'Sack':

                    if play['yards_gained'] >= 16:

                        temp['explosive_pass'] = 1

                    else:

                        temp['explosive_pass'] = 0
            else:

                temp['opportunity'] = 0

            if play['down'] == 1:
                if play['yards_gained'] >= 0.5 * play['distance']:
                    temp['success'] = 1
                    temp['first_down_success'] = 1

                    if play['play_type'] == 'Rush':
                        temp['first_down_rush_success'] = 1
                        temp['standard_down_rush_success'] = 1

                    elif play['play_type'].startswith('Pass') or play['play_type'] == 'Sack':
                        temp['first_down_pass_success'] = 1
                        temp['standard_down_pass_success'] = 1
                else:
                    temp['success'] = 0
                    temp['first_down_success'] = 0

                    if play['play_type'] == 'Rush':

                        temp['first_down_rush_success'] = 0
                        temp['standard_down_rush_success'] = 0

                    elif play['play_type'].startswith('Pass') or play['play_type'] == 'Sack':
                        temp['first_down_pass_success'] = 0
                        temp['standard_down_pass_success'] = 0

            elif play['down'] == 2:
                if play['yards_gained'] >= 0.7 * play['distance']:
                    temp['success'] = 1
                    temp['second_down_success'] = 1

                    if play['play_type'] == 'Rush':
                        temp['second_down_rush_success'] = 1
                        if play['distance'] >= 8:
                            temp['passing_down_rush_success'] = 1
                        else:
                            temp['standard_down_rush_success'] = 1

                    elif play['play_type'].startswith('Pass') or play['play_type'] == 'Sack':
                        temp['second_down_pass_success'] = 1
                        if play['distance'] >= 8:
                            temp['passing_down_pass_success'] = 1
                        else:
                            temp['standard_down_pass_success'] = 1

                else:
                    temp['success'] = 0
                    temp['second_down_success'] = 0

                    if play['play_type'] == 'Rush':
                        temp['second_down_rush_success'] = 0
                        if play['distance'] >= 8:
                            temp['passing_down_rush_success'] = 0
                        else:
                            temp['standard_down_rush_success'] = 0

                    elif play['play_type'].startswith('Pass') or play['play_type'] == 'Sack':
                        temp['second_down_pass_success'] = 0
                        if play['distance'] >= 8:
                            temp['passing_down_pass_success'] = 0
                        else:
                            temp['standard_down_pass_success'] = 0

            elif play['down'] == 3:
                if play['yards_gained'] >= play['distance'] or play['play_type'].lower() == 'punt' or play[
                    'play_type'].lower() == 'field goal good':
                    temp['success'] = 1
                    temp['third_down_success'] = 1

                    if play['play_type'] == 'Rush':
                        temp['third_down_rush_success'] = 1

                        if play['distance'] <= 2:
                            temp['power_down_rush_success'] = 1
                        elif play['distance'] < 5:
                            temp['standard_down_rush_success'] = 1
                        else:
                            temp['passing_down_rush_success'] = 1

                    elif play['play_type'].startswith('Pass') or play['play_type'] == 'Sack':
                        temp['third_down_pass_success'] = 1

                        if play['distance'] <= 2:
                            temp['power_down_pass_success'] = 1
                        elif play['distance'] < 5:
                            temp['standard_down_pass_success'] = 1
                        else:
                            temp['passing_down_pass_success'] = 1

                else:
                    temp['success'] = 0

                    if play['play_type'] == 'Rush':
                        temp['third_down_rush_success'] = 0

                        if play['distance'] <= 2:
                            temp['power_down_rush_success'] = 0
                        elif play['distance'] < 5:
                            temp['standard_down_rush_success'] = 0
                        else:
                            temp['passing_down_rush_success'] = 0

                    elif play['play_type'].startswith('Pass') or play['play_type'] == 'Sack':
                        temp['third_down_pass_success'] = 0

                        if play['distance'] <= 2:
                            temp['power_down_pass_success'] = 0
                        elif play['distance'] < 5:
                            temp['standard_down_pass_success'] = 0
                        else:
                            temp['passing_down_pass_success'] = 0

            elif play['down'] == 4:
                if play['yards_gained'] >= play['distance'] or play['play_type'].lower() == 'punt' or play[
                    'play_type'].lower() == 'field goal good':
                    temp['success'] = 1
                    temp['fourth_down_success'] = 1

                    if play['play_type'] == 'Rush':
                        temp['fourth_down_rush_success'] = 1

                        if play['distance'] <= 2:
                            temp['power_down_rush_success'] = 1
                        elif play['distance'] < 5:
                            temp['standard_down_rush_success'] = 1
                        else:
                            temp['passing_down_rush_success'] = 1

                    elif play['play_type'].startswith('Pass') or play['play_type'] == 'Sack':
                        temp['fourth_down_pass_success'] = 1

                        if play['distance'] <= 2:
                            temp['power_down_pass_success'] = 1
                        elif play['distance'] < 5:
                            temp['standard_down_pass_success'] = 1
                        else:
                            temp['passing_down_pass_success'] = 1

                else:
                    temp['success'] = 0
                    if play['play_type'] == 'Rush':
                        temp['fourth_down_rush_success'] = 0

                        if play['distance'] <= 2:
                            temp['power_down_rush_success'] = 0
                        elif play['distance'] < 5:
                            temp['standard_down_rush_success'] = 0
                        else:
                            temp['passing_down_rush_success'] = 0

                    elif play['play_type'].startswith('Pass') or play['play_type'] == 'Sack':
                        temp['fourth_down_pass_success'] = 0

                        if play['distance'] <= 2:
                            temp['power_down_pass_success'] = 0
                        elif play['distance'] < 5:
                            temp['standard_down_pass_success'] = 0
                        else:
                            temp['passing_down_pass_success'] = 0

            else:
                temp['success'] = -1

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
        categories = ('success',
                      'first_down_success',
                      'first_down_rush_success',
                      'first_down_pass_success',
                      'second_down_success',
                      'second_down_rush_success',
                      'second_down_pass_success',
                      'third_down_success',
                      'third_down_rush_success',
                      'third_down_pass_success',
                      'fourth_down_success',
                      'fourth_down_rush_success',
                      'fourth_down_pass_success',
                      'standard_down_rush_success',
                      'standard_down_pass_success',
                      'passing_down_rush_success',
                      'passing_down_pass_success',
                      'power_down_rush_success',
                      'power_down_pass_success',
                      'run_stuff',
                      'explosive_rush',
                      'explosive_pass',
                      'opportunity'
                      )
        for c in categories:
            out = []
            for p in self.labeled:
                if c in p.keys():
                    if p['home'] == p['offense']:
                        row = [p['home'] + ' offense', p['away'] + ' defense']
                        if p[c] == 1:
                            row.extend(['H', p['week']])
                        else:
                            row.extend(['A', p['week']])
                    else:
                        row = [p['home'] + ' defense', p['away'] + ' offense']
                        if p[c] == 1:
                            row.extend(['A', p['week']])
                        else:
                            row.extend(['H', p['week']])

                    out.append(row)
            with open(os.path.join('data', '{}.csv'.format(c)), 'w+', newline='') as outfile:
                csvr = csv.writer(outfile)
                csvr.writerows(out)
