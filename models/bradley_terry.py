import functools
import random
from typing import Dict, Tuple

import numpy as np
import statsmodels.api as sm

from pull_scripts import pull_season
from shared_types import *


class Indexer(object):
    def __init__(self):
        self.ind = dict()

    # TODO: Can I overload something?
    def get(self, __name: str) -> int:
        return self.ind[__name]

    def __len__(self) -> int:
        return len(self.ind)

    def push(self, name: str) -> None:
        if name in self.ind:
            return

        self.ind[name] = len(self.ind)


@functools.lru_cache(100)
def log_reg(year: Year) -> Tuple[LogRegType, Indexer]:
    ind_school = Indexer()
    num_data_pts = 0
    for game in pull_season.scrape_season(year):
        ind_school.push(game.winner)
        ind_school.push(game.loser)
        num_data_pts += 1
    
    X, y = np.zeros((num_data_pts, len(ind_school))), list()
    for i, game in enumerate(pull_season.scrape_season(year)):
        target_winner = random.random() < 0.5
        if target_winner:
            X[i, ind_school.get(game.winner)] = 1
            X[i, ind_school.get(game.loser)] = -1
            y.append(1)
        else:
            X[i, ind_school.get(game.winner)] = -1
            X[i, ind_school.get(game.loser)] = 1
            y.append(0)

    print(X)
    print(X.shape)
    print(y)
    model = sm.Logit(y, X).fit()
    return model, ind_school


def bt_featurizer(game: PlayoffGame) -> Dict[str, float]:
    model, ind_school = log_reg(game.year)
    X = np.zeroes((1, len(ind_school)))
    X[0, ind_school.get(game.team_1_school)] = 1
    X[0, ind_school.get(game.team_2_school)] = -1
    y = model.predict(X)
    return {"bt": y}
