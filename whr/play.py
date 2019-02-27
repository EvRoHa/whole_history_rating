import sys


class Play:

    def __init__(self, home, away, winner, time_step, handicap=0):
        self.week = time_step
        self.away_team = away
        self.home_team = home
        self.winner = winner
        self.handicap = handicap
        self.handicap_proc = handicap
        self.apd = None
        self.hpd = None

    def opponents_adjusted_gamma(self, team):
        if team == self.away_team:
            opponent_elo = self.hpd.elo() + self.handicap
        elif team == self.home_team:
            opponent_elo = self.apd.elo() - self.handicap
        else:
            raise (AttributeError(
                f"No opponent for {team.__str__()}, since they're not in this play: {self.__str__()}."))
        rval = 10 ** (opponent_elo / 400.0)
        if rval == 0 or rval > sys.maxsize:
            raise (AttributeError("bad adjusted gamma"))
        return rval

    def opponent(self, team):
        if team == self.away_team:
            return self.home_team
        elif team == self.home_team:
            return self.away_team

    def prediction_score(self):
        if self.away_win_probability() == 0.5:
            return 0.5
        else:
            return 1.0 if ((self.winner == "W" and self.away_win_probability() > 0.5) or (
                    self.winner == "B" and self.away_win_probability() < 0.5)) else 0.0

    def inspect(self):
        return "{} : A:{}(r={}) H:{}(r={}) winner = {}, handicap = {}".format(self.__str__(), self.away_team.name,
                                                                              self.apd.r if self.apd is not None else '?',
                                                                              self.home_team.name,
                                                                              self.hpd.r if self.hpd is not None else '?',
                                                                              self.winner, self.handicap)

    def away_win_probability(self):
        return self.apd.gamma() / (self.apd.gamma() + self.opponents_adjusted_gamma(self.away_team))

    def home_win_probability(self):
        return self.hpd.gamma() / (self.hpd.gamma() + self.opponents_adjusted_gamma(self.home_team))
