import math
import sys

import numpy as np

from whr.teamweek import TeamWeek


class Team():

    def __init__(self, name, config):
        self.name = name
        self.w2 = (math.sqrt(config["w2"]) * math.log(10) / 400) ** 2  # Convert from elo^2 to r^2
        self.weeks = []

    def log_likelihood(self):
        result = 0.0
        sigma2 = self.compute_sigma2()
        n = len(self.weeks)
        for i in range(n):
            prior = 0
            if i < (n - 1):
                rd = self.weeks[i].r - self.weeks[i + 1].r
                prior += (1 / math.sqrt(2 * math.pi))
            if i > 0:
                rd = self.weeks[i].r - self.weeks[i - 1].r
                prior += (1 / (math.sqrt(2 * math.pi *
                                         sigma2[i - 1]))) * math.exp(-(rd ** 2) / 2 * sigma2[i - 1])
            if prior == 0:
                result += self.weeks[i].log_likelihood()
            else:
                if self.weeks[i].log_likelihood() >= sys.maxsize or math.log(prior) >= sys.maxsize:
                    print(
                        "Infinity at {}: {} + {}: prior = {}, weeks = {}".format(self.__str__(),
                                                                                 self.weeks[i].log_likelihood(),
                                                                                 math.log(prior), prior, self.weeks))
                    return
                result += self.weeks[i].log_likelihood() + math.log(prior)
        return result

    @staticmethod
    def hessian(weeks, sigma2):
        n = len(weeks)
        mat = np.zeros((n, n))
        for row in range(n):
            for col in range(n):
                if row == col:
                    prior = 0
                    if row < (n - 1):
                        prior += -1.0 / sigma2[row]
                    if row > 0:
                        prior += -1.0 / sigma2[row - 1]
                    mat[row, col] = weeks[row].log_likelihood_second_derivative() + \
                                    prior - 0.001
                elif row == col - 1:
                    mat[row, col] = 1.0 / sigma2[row]
                elif row == col + 1:
                    mat[row, col] = 1.0 / sigma2[col]
                else:
                    mat[row, col] = 0
        return mat

    @staticmethod
    def gradient(r, weeks, sigma2):
        g = []
        n = len(weeks)
        for idx, week in enumerate(weeks):
            prior = 0
            if idx < (n - 1):
                prior += -(r[idx] - r[idx + 1]) / sigma2[idx]
            if idx > 0:
                prior += -(r[idx] - r[idx - 1]) / sigma2[idx - 1]
            g.append(week.log_likelihood_derivative() + prior)
        return g

    def run_one_newton_iteration(self):
        for week in self.weeks:
            week.clear_play_terms_cache()
        if len(self.weeks) == 1:
            self.weeks[0].update_by_1d_newtons_method()
        elif len(self.weeks) > 1:
            self.update_by_ndim_newton()

    def compute_sigma2(self):
        sigma2 = []
        for d1, d2 in zip(*(self.weeks[i:] for i in range(2))):
            sigma2.append(abs(d2.week - d1.week) * self.w2)
        return sigma2

    def update_by_ndim_newton(self):
        # r
        r = [d.r for d in self.weeks]

        # sigma squared (used in the prior)
        sigma2 = self.compute_sigma2()

        h = self.hessian(self.weeks, sigma2)
        g = self.gradient(r, self.weeks, sigma2)
        n = len(r)
        a = np.zeros((n,))
        d = np.zeros((n,))
        b = np.zeros((n,))
        d[0] = h[0, 0]
        b[0] = h[0, 1]

        for i in range(1, n):
            a[i] = h[i, i - 1] / d[i - 1]
            d[i] = h[i, i] - a[i] * b[i - 1]
            if i < n - 1:
                b[i] = h[i, i + 1]

        y = np.zeros((n,))
        y[0] = g[0]
        for i in range(1, n):
            y[i] = g[i] - a[i] * y[i - 1]

        x = np.zeros((n,))
        x[n - 1] = y[n - 1] / d[n - 1]
        for i in range(n - 2, -1, -1):
            x[i] = (y[i] - b[i] * x[i + 1]) / d[i]

        new_r = [ri - xi for ri, xi in zip(r, x)]

        for r in new_r:
            if r > 650:
                # raise UnstableRatingException, "Unstable r (#{new_r}) on player #{inspect}"
                raise Exception("unstable r on player")

        for idx, week in enumerate(self.weeks):
            week.r = week.r - x[idx]

    def covariance(self):
        r = [d.r for d in self.weeks]

        sigma2 = self.compute_sigma2()
        h = self.hessian(self.weeks, sigma2)
        #g = self.gradient(r, self.weeks, sigma2)
        n = len(r)

        a = np.zeros((n,))
        d = np.zeros((n,))
        b = np.zeros((n,))
        d[0] = h[0, 0]
        b[0] = h[0, 1] if h.size > 2 else 0

        for i in range(1, n):
            a[i] = h[i, i - 1] / d[i - 1]
            d[i] = h[i, i] - a[i] * b[i - 1]
            if i < n - 1:
                b[i] = h[i, i + 1]

        dp = np.zeros((n,))
        dp[n - 1] = h[n - 1, n - 1]
        bp = np.zeros((n,))
        bp[n - 1] = h[n - 1, n - 2]
        ap = np.zeros((n,))
        for i in range(n - 2, -1, -1):
            ap[i] = h[i, i + 1] / dp[i + 1]
            dp[i] = h[i, i] - ap[i] * bp[i + 1]
            if i > 0:
                bp[i] = h[i, i - 1]

        v = np.zeros((n,))
        for i in range(n - 1):
            v[i] = dp[i + 1] / (b[i] * bp[i + 1] - d[i] * dp[i + 1])
        v[n - 1] = -1 / d[n - 1]

        mat = np.zeros((n, n))
        for row in range(n):
            for col in range(n):
                if row == col:
                    mat[row, col] = v[row]
                elif row == col - 1:
                    mat[row, col] = -1 * a[col] * v[col]
                else:
                    mat[row, col] = 0

        return mat

    def update_uncertainty(self):
        if len(self.weeks) > 0:
            c = self.covariance()
            u = [c[i, i] for i in range(len(self.weeks))]  # u = variance
            for i, d in enumerate(self.weeks):
                d.uncertainty = u[i]
            return None
        else:
            return 5

    def add_play(self, play):
        if len(self.weeks) == 0 or self.weeks[-1].week != play.week:
            new_tweek = TeamWeek(self, play.week)
            if len(self.weeks) == 0:
                new_tweek.is_first_week = True
                new_tweek.set_gamma(1)
            else:
                new_tweek.set_gamma(self.weeks[-1].gamma())
            self.weeks.append(new_tweek)
        if play.away_team == self:
            play.apd = self.weeks[-1]
        else:
            play.hpd = self.weeks[-1]
        self.weeks[-1].add_play(play)
