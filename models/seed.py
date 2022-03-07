from typing import Dict, List

import pandas as pd
from sklearn.linear_model import LogisticRegression

from pull_scripts import pull_round_1
from shared_types import *


def seed_featurizer(game: PlayoffGame) -> Dict[str, float]:
    return {f"{i}_seed": 1 if game.school_1_seed == i else 0 for i in range(1, 17)}


def _infer_single_game(model: LogRegType, game: PlayoffGame) -> float:
    # Average P(win) and 1-P(loss) to smooth some models.
    p = model.predict_proba(pd.DataFrame(data=[seed_featurizer(game)]))[0, 1]
    q = model.predict_proba(pd.DataFrame(data=[seed_featurizer(game.flip())]))[0, 1]
    return (p + 1 - q) / 2.0


def infer(model: LogRegType, years: List[Year]) -> Dict[PlayoffGame, float]:
    assert len(years) > 0

    result = dict()
    for year in years:
        for game in pull_round_1.read_playoffs(year):
            result[game] = _infer_single_game(model, game)
    return result


def train_model(years: List[Year]) -> LogisticModel:
    assert len(years) > 0

    X_rows = list()
    y = list()
    for year in years:
        for game in pull_round_1.read_playoffs(year):
            X_rows.append(seed_featurizer(game))
            y.append(1 if game.school_1_won else 0)
    X = pd.DataFrame(data=X_rows)

    model = LogisticRegression().fit(X, y)
    return model
