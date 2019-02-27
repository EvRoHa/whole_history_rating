import csv
import json
import math
import time
from collections import defaultdict

from whr.play import Play
from whr.team import Team


class UnstableRatingException(Exception):
    pass


class Base:

    def __init__(self, config=None):
        if config is None:
            self.config = defaultdict(lambda: None)
        else:
            self.config = config
            if self.config.get("debug") is None:
                self.config["debug"] = False
        if self.config.get("w2") is None:
            self.config["w2"] = 300.0
        self.plays = []
        self.teams = {}

    def print_ordered_ratings(self, current=False):
        """displays all ratings for each team (for each week in the season) ordered
        """
        teams = [x for x in self.teams.values() if len(x.weeks) > 0]
        teams.sort(key=lambda x: x.weeks[-1].gamma())
        for t in teams:
            if len(t.weeks) > 0:
                if current:
                    print("{} => {}".format(t.name, t.weeks[-1].elo()))
                else:
                    print("{} => {}".format(t.name, [x.elo() for x in t.weeks]))

    def get_ordered_ratings(self, current=False, compact=False):
        """gets all ratings for each team (for each week in the season) ordered
        
        Returns:
            list[list[float]]: for each team and each week in the season, the corresponding elo
        
        Args:
            current (bool, optional): True to let only the last estimation of the elo, False gets all estimation for each week played
            compact (bool, optional): True to get only a list of elos, False to get the name before
        """
        result = []
        teams = [x for x in self.teams.values() if len(x.weeks) > 0]
        teams.sort(key=lambda x: x.weeks[-1].gamma())
        for t in teams:
            if len(t.weeks) > 0:
                if current:
                    result.append((t.name, t.weeks[-1].elo()))
                elif compact:
                    result.append([x.elo() for x in t.weeks])
                else:
                    result.append((t.name, [x.elo() for x in t.weeks]))
        return result

    def log_likelihood(self):
        """gets the likelihood of the current state

        in general, more iterations give a higher likelihood
        
        Returns:
            float: the likelihood
        """
        score = 0.0
        for t in self.teams.values():
            if len(t.weeks) > 0:
                score += t.log_likelihood()
        return score

    def team_by_name(self, name):
        """gets the team object corresponding to the name
        
        Args:
            name (str): the name of the team
        
        Returns:
            team: the corresponding team
        """
        if self.teams.get(name, None) is None:
            self.teams[name] = Team(name, self.config)
        return self.teams[name]

    def ratings_for_team(self, name, current=False):
        """gets all rating for each day played for the team
        
        Args:
            name (str): the team's name
        
        Returns:
            list[list[int,float,float]]: for each week, the time_step the elo the uncertainty
        """
        team = self.team_by_name(name)
        if current:
            return (round(team.weeks[-1].elo()), round(team.weeks[-1].uncertainty * 100))
        else:
            return [[w.week, round(w.elo()), round(w.uncertainty * 100)] for w in team.weeks]

    def _setup_play(self, home, away, winner, time_step):
        if home == away:
            raise (AttributeError("Invalid play (home team == away team)"))
        away_team = self.team_by_name(away)
        home_team = self.team_by_name(home)
        play = Play(home_team, away_team, winner, time_step)
        return play

    def create_play(self, home, away, winner, time_step):
        """creates a new play to be added to the base
        
        Args:
            home (str): the home name
            away (str): the away name
            winner (str): "B" if home won, "W" if away won
            time_step (int): the day of the match from origin

        Returns:
            Play: the added play
        """
        play = self._setup_play(home, away, winner, time_step)
        return self._add_play(play)

    def _add_play(self, play):
        play.away_team.add_play(play)
        play.home_team.add_play(play)
        if play.hpd is None:
            print("Bad play")
        self.plays.append(play)
        return play

    def iterate(self, count):
        """do a number of "count" iterations of the algorithm
        
        Args:
            count (int): the number of iterations desired
        """
        for _ in range(count):
            self._run_one_iteration()
        for name, team in self.teams.items():
            team.update_uncertainty()

    def auto_iterate(self, time_limit=10, precision=10E-3):
        """Summary
        
        Args:
            time_limit (int, optional): the maximal time after which no more iteration are launched
            precision (float, optional): the precision of the stability desired
        
        Returns:
            tuple(int, bool): the number of iterations and True if it has reached stability, False otherwise
        """
        start = time.time()
        self.iterate(10)
        a = self.get_ordered_ratings(compact=True)
        i = 10
        while True:
            self.iterate(10)
            i += 10
            b = self.get_ordered_ratings(compact=True)
            if self._test_stability(a, b, precision):
                return i, True
            if time.time() - start > time_limit:
                return i, False
            a = b

    def _test_stability(self, v1, v2, precision=10E-3):
        """tests if two lists of lists of floats are equal but a certain precision
        
        Args:
            v1 (list[list[float]]): first list containing ints
            v2 (list[list[float]]): second list containing ints
            precision (float, optional): the precision after which v1 and v2 are not equal
        
        Returns:
            bool: True if the two lists are close enough, False otherwise
        """
        v1 = [x for y in v1 for x in y]
        v2 = [x for y in v2 for x in y]
        for x1, x2 in zip(v1, v2):
            if abs(x2 - x1) > precision:
                return False
        return True

    def probability_future_match(self, name1, name2):
        """gets the probability of winning for an hypothetical match against name1 and name2

        displays the probability of winning for name1 and name2 in percent rounded to the second decimal

        Args:
          name1 (str): name1's name
          name2 (str): name2's name

        Returns:
          tuple(int,int): the probability between 0 and 1 for name1 first then name2
        """
        # Avoid self-played plays (no info)
        if name1 == name2:
            raise (AttributeError("Invalid play (home == away)"))
        team1 = self.team_by_name(name1)
        team2 = self.team_by_name(name2)
        hpd_gamma = 1
        hpd_elo = (math.log(1) * 400) / (math.log(10))
        apd_gamma = 1
        apd_elo = (math.log(1) * 400) / (math.log(10))
        if len(team1.weeks) > 0:
            hpd = team1.weeks[-1]
            hpd_gamma = hpd.gamma()
            hpd_elo = hpd.elo()
        if len(team2.weeks) != 0:
            apd = team2.weeks[-1]
            apd_gamma = apd.gamma()
            apd_elo = apd.elo()
        team1_prob = hpd_gamma / (hpd_gamma + 10 ** ((apd_elo) / 400.0))
        team2_prob = apd_gamma / (apd_gamma + 10 ** ((hpd_elo) / 400.0))
        print("win probability: {}:{:10.2f}; {}:{:10.2f}".format(name1, team1_prob, name2, team2_prob))
        return team1_prob, team2_prob

    def _run_one_iteration(self):
        """runs one iteration of the whr algorithm
        """
        for name, team in self.teams.items():
            team.run_one_newton_iteration()

    def load_plays(self, games, separator=','):
        """loads all games at once

        given a string representing the path of a file or a list of string representing all games,
        this function loads all games in the base
        all match must comply to this format:
            "home_name away_name winner time_step"
            home_name is required
            away_name is required

            winner is H or A is required
            time_step is required
        Args:
            games (str|list[str]): Description
        """
        if isinstance(games, str):
            with open(games, 'r') as f:
                data = f.readlines()
        else:
            data = games
        for line in data:
            home, away, winner, time_step = line[0], line[1], line[2], line[3]
            time_step = int(time_step)

            self.create_play(home, away, winner, time_step)

    def save_base(self, path):
        """saves the current state of the base to a file at "path"
        
        Args:
            path (str): the path where to save the base
        """
        json.dump([self.teams, self.plays, self.config["w2"]], open(path, 'wb'))

    @staticmethod
    def load_base(path):
        """loads a saved base
        
        Args:
            path (str): the path to the saved base
        
        Returns:
            Base: the loaded base
        """
        teams, plays, config = json.load(open(path, 'rb'))
        result = Base()
        result.config["w2"], result.plays, result.teams = config, plays, teams
        return result


if __name__ == "__main__":
    whr = Base(config={"w2": 14})
    with open('processed plays.csv', 'r') as infile:
        plays = [x for x in csv.reader(infile)]

    whr.load_plays(plays)
    print(whr.auto_iterate())

    #    print(whr.ratings_for_team("ohio state offense"))
    #    print(whr.ratings_for_team("ohio state defense"))
    #    print(whr.probability_future_match("ohio state offense", "nobody2"))
    #    print(whr.log_likelihood())
    #    whr.print_ordered_ratings()
    whr.print_ordered_ratings(current=True)
