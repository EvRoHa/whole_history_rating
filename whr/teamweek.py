import math
import sys


class TeamWeek:

    def __init__(self, team, week):
        self.r = None
        self.week = week
        self.team = team
        self.is_first_week = False
        self.won_plays = []
        self.lost_plays = []

    def set_gamma(self, value):
        self.r = math.log(value)

    def gamma(self):
        return math.exp(self.r)

    def set_elo(self, value):
        self.r = value * (math.log(10) / 400)

    def elo(self):
        return (self.r * 400) / (math.log(10))

    def clear_play_terms_cache(self):
        self._won_play_terms = None
        self._lost_play_terms = None

    def won_play_terms(self):
        if self._won_play_terms is None:
            self._won_play_terms = []
            for g in self.won_plays:
                other_gamma = g.opponents_adjusted_gamma(self.team)
                if other_gamma == 0 or other_gamma is None or other_gamma > sys.maxsize:
                    print(f"other_gamma ({g.opponent(self.team).__str__()}) = {other_gamma}")
                self._won_play_terms.append([1.0, 0.0, 1.0, other_gamma])
            if self.is_first_week:
                # win against virtual team ranked with gamma = 1.0
                self._won_play_terms.append([1.0, 0.0, 1.0, 1.0])
        return self._won_play_terms

    def lost_play_terms(self):
        if self._lost_play_terms is None:
            self._lost_play_terms = []
            for g in self.lost_plays:
                other_gamma = g.opponents_adjusted_gamma(self.team)
                if other_gamma == 0 or other_gamma is None or other_gamma > sys.maxsize:
                    print("other_gamma ({}) = {}".format(g.opponent(self.team).__str__(), other_gamma))
                self._lost_play_terms.append([0.0, other_gamma, 1.0, other_gamma])
            if self.is_first_week:
                # win against virtual team ranked with gamma = 1.0
                self._lost_play_terms.append([0.0, 1.0, 1.0, 1.0])
        return self._lost_play_terms

    def log_likelihood_second_derivative(self):
        result = 0.0
        for a, b, c, d in self.won_play_terms() + self.lost_play_terms():
            result += (c * d) / ((c * self.gamma() + d) ** 2.0)
        return -1 * self.gamma() * result

    def log_likelihood_derivative(self):
        tally = 0.0
        for a, b, c, d in (self.won_play_terms() + self.lost_play_terms()):
            tally += c / (c * self.gamma() + d)
        return len(self.won_play_terms()) - self.gamma() * tally

    def log_likelihood(self):
        tally = 0.0
        for a, b, c, d in self.won_play_terms():
            tally += math.log(a * self.gamma())
            tally -= math.log(c * self.gamma() + d)
        for a, b, c, d in self.lost_play_terms():
            tally += math.log(b)
            tally -= math.log(c * self.gamma() + d)
        return tally

    def add_play(self, play):
        if (play.winner == "A" and play.away_team == self.team) or (
                play.winner == "H" and play.home_team == self.team):
            self.won_plays.append(play)
        else:
            self.lost_plays.append(play)

    def update_by_1d_newtons_method(self):
        dr = (self.log_likelihood_derivative() /
              self.log_likelihood_second_derivative())
        new_r = self.r - dr
        self.r = new_r
