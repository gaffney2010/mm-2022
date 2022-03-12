################################################################################
# Logging logic, must come first
from constants import DATA_DIR
from tools.logger import configure_logging
import logging

configure_logging(
    screen=False, file=True, screen_level=logging.DEBUG, file_level=logging.WARNING
)
################################################################################

# This emulates the code in bradley_terry.py
import json
import os
import random
from typing import Iterator

import attr
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from models import bradley_terry
from pull_scripts import pull_season
from shared_types import *


@attr.s(frozen=True)
class ConfMatch(object):
    winner_conf: Conf = attr.ib()
    loser_conf: Conf = attr.ib()


def conference_matches(year: Year) -> Iterator[Conf]:
    conf = pull_season.get_conf(year)
    for game in pull_season.scrape_season(year):
        if game.winner not in conf:
            logging.debug(f"No key for {game.winner}")
            continue
        if game.loser not in conf:
            logging.debug(f"No key for {game.loser}")
            continue
        winner_conf, loser_conf = conf[game.winner], conf[game.loser]
        if winner_conf == loser_conf:
            logging.debug("Same conference")
            continue
        yield ConfMatch(winner_conf=winner_conf, loser_conf=loser_conf)


def conf_bt_season(year: Year) -> Dict[School, float]:
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

    result = dict()
    for k, v in ind_conf.ind.items():
        result[k] = model.coef_[0][v]
    return result


def cached_conf_bt_season(year: Year, version: str) -> Dict[School, float]:
    # Version for easy cache invalidation - kinda hack.
    cache_key = f"cached_conf_bt_season.{version}.{year}.json.data"
    path = os.path.join(DATA_DIR, cache_key)

    if os.path.exists(path):
        with open(path, "r") as f:
            json_str = f.read()
        return json.loads(json_str)

    result = conf_bt_season(year)
    with open(path, "w") as f:
        f.write(json.dumps(result))
    return result


version = "1"
data = list()
for year in range(1990, 2023):
    for school, coef in cached_conf_bt_season(year, version).items():
        datum = {
            "year": year,
            "school": school,
            "coef": coef,
        }
        data.append(datum)

df = pd.DataFrame(data)
df.to_csv(f"conf_trend.csv")
