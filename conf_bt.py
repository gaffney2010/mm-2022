# This emulates the code in bradley_terry.py
import random
from typing import Any, Iterator

import attr
import numpy as np
from sklearn.linear_model import LogisticRegression

from models import bradley_terry
from pull_scripts import pull_season
from shared_types import *


@attr.s(frozen=True)
class ConfMatch(object):
    winner_conf: Conf = attr.ib()
    loser_conf: Conf = attr.ib()


def _na(x: Any) -> bool:
    return x == "" or x != x


def conference_matches(year: Year) -> Iterator[Conf]:
    conf = pull_season.get_conf(year)
    for game in pull_season.scrape_season(year):
        if game.winner not in conf:
            # TODO: print -> logging statements
            print(f"No key for {game.winner}")
            continue
        if game.loser not in conf:
            print(f"No key for {game.loser}")
            continue
        winner_conf, loser_conf = conf[game.winner], conf[game.loser]
        if winner_conf == loser_conf:
            print("Same conference")
            continue
        yield ConfMatch(winner_conf=winner_conf, loser_conf=loser_conf)


year = 2021

# Need this as a list actually:
matches = list(conference_matches(year))

ind_conf = bradley_terry.Indexer()
for match in matches:
    ind_conf.push(match.winner_conf)
    ind_conf.push(match.winner_conf)
num_data_pts = len(matches)

X, y = np.zeros((num_data_pts, len(ind_conf))), list()
for i, match in enumerate(matches):
    target_winner = random.random() < 0.5
    if target_winner:
        X[i, ind_conf.get(match.winner_conf)] = 1
        X[i, ind_conf.get(match.loser_conf)] = -1
        y.append(1)
    else:
        X[i, ind_conf.get(match.winner_conf)] = -1
        X[i, ind_conf.get(match.loser_conf)] = 1
        y.append(0)

model = LogisticRegression().fit(X, y)

for k, v in ind_conf.ind.items():
    print(f"{k}: {model.coef_[0][v]}")
