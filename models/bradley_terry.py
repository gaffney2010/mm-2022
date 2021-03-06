import functools
import pickle
import random
from typing import Dict, List, Tuple

import numpy as np
from sklearn.linear_model import LogisticRegression

from constants import *
from pull_scripts import pull_season, pull_round_1
from shared_types import *


class Indexer(object):
    def __init__(self):
        self.ind = dict()

    def __getitem__(self, name: str) -> Any:
        return self.ind[name]

    def __len__(self) -> int:
        return len(self.ind)

    def push(self, name: str) -> None:
        if name in self.ind:
            return

        self.ind[name] = len(self.ind)


@functools.lru_cache(100)
def log_reg(year: Year, with_const: bool = False) -> Tuple[LogRegType, Indexer]:
    ind_school = Indexer()
    for game in pull_season.scrape_season(year):
        ind_school.push(game.winner)
        ind_school.push(game.loser)
    num_data_pts = len(pull_season.scrape_season(year))
    num_feats = len(ind_school) + (1 if with_const else 0)

    X, y = np.zeros((num_data_pts, num_feats)), list()
    for i, game in enumerate(pull_season.scrape_season(year)):
        target_winner = random.random() < 0.5
        if target_winner:
            X[i, ind_school[game.winner]] = 1
            X[i, ind_school[game.loser]] = -1
            y.append(1)
        else:
            X[i, ind_school[game.winner]] = -1
            X[i, ind_school[game.loser]] = 1
            y.append(0)
        if with_const:
            X[i, num_feats-1] = 1

    model = LogisticRegression().fit(X, y)
    return model, ind_school


def log_reg_with_hd_save(year: Year, with_const: bool = False) -> Tuple[LogRegType, Indexer]:
    # Version for easy cache invalidation - kinda hack.
    VERSION = 1
    wconst = "_with_const" if with_const else ""
    cache_key = f"log_reg_with_hd_save{wconst}.{VERSION}.{year}.json.data"
    path = os.path.join(DATA_DIR, cache_key)

    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)

    result = log_reg(year, with_const=with_const)
    with open(path, "wb") as f:
        pickle.dump(result, f)
    return result


def bt(game: PlayoffGame, with_const: bool = False, with_hd_save: bool = False) -> float:
    if with_hd_save:
        model, ind_school = log_reg_with_hd_save(game.year, with_const)
    else:
        model, ind_school = log_reg(game.year, with_const)

    num_feats = len(ind_school) + (1 if with_const else 0)
    X = np.zeros((1, num_feats))
    X[0, ind_school[game.school_1]] = 1
    X[0, ind_school[game.school_2]] = -1
    if with_const:
        X[0, num_feats-1] = 1
    y = model.predict_proba(X)[0, 1]
    return y


def history(years: List[Year]) -> Dict[PlayoffGame, float]:
    result = dict()
    for year in years:
        for game in pull_round_1.read_playoffs(year):
            result[game] = bt(game)
    return result
