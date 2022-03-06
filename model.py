import logging
from typing import Dict, List

import pandas as pd
import statsmodels.api as sm

import pull_round_1
from shared_types import *


def train_model(featurizer: Featurizer, years: List[Year]) -> LogisticModel:
    assert(len(years) > 0)

    X_rows = list()
    y = list()
    for year in years:
        for game in pull_round_1.read_playoffs(year):
            X_rows.append(featurizer(game))
            y.append(1 if game.school_1_won else 0)
    X = pd.DataFrame(data=X_rows)

    model = sm.Logit(y, X).fit()

    return LogisticModel(featurizer=featurizer, model=model)


def _infer(model: LogisticModel, years: List[Year]) -> Dict[PlayoffGame, float]:
    raise NotImplementedError


def _report_cross_entropy(history: Dict[PlayoffGame, float]) -> str:
    raise NotImplementedError


def _report_calibration(history: Dict[PlayoffGame, float], bins: int = 5) -> str:
    raise NotImplementedError


def score_and_report(model: LogisticModel, years: List[Year]) -> None:
    history = _infer(model, years)
    logging.info(_report_cross_entropy(history))
    logging.info(_report_calibration(history))


# Seed model
def seed_featurizer(game: PlayoffGame) -> Dict[str, float]:
    return {
        f"{i}_seed": 1 if game.school_1_seed == i else 0
        for i in range(1, 17)
    }


print(train_model(seed_featurizer, [2021] + list(range(2019, 1984, -1))).model.summary())
