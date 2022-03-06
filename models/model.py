import collections
from typing import Dict, List

import pandas as pd
import statsmodels.api as sm
from tabulate import tabulate

from pull_scripts import pull_round_1
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


def _infer_single_game(model: LogisticModel, game: PlayoffGame) -> float:
    # Average P(win) and 1-P(loss) to smooth some models.
    p = model.model.predict(pd.DataFrame(data=[model.featurizer(game)]))
    q = model.model.predict(pd.DataFrame(data=[model.featurizer(game.flip())]))
    return (p + 1 - q) / 2.0


def _infer(model: LogisticModel, years: List[Year]) -> Dict[PlayoffGame, float]:
    assert(len(years) > 0)

    result = dict()
    for year in years:
        for game in pull_round_1.read_playoffs(year):
            result[game] = _infer_single_game(model, game)
    return result


# TODO: This isn't actually cross entropy
def _report_cross_entropy(history: Dict[PlayoffGame, float]) -> str:
    num, den = 0, 0
    for act, pred in history.items():
        num += 1-pred if act.school_1_won else pred
        den += 1
    return f"Cross-entropy: {num/den}"


def _report_calibration(history: Dict[PlayoffGame, float], bins: int = 5) -> str:
    binning = collections.defaultdict(list)
    for act, pred in history.items():
        bin = int(pred * bins)
        binning[bin].append((act, pred))
    
    df_rows = list()
    for bin in range(bins):
        games = binning[bin]
        act_num, pred_num, den = 0, 0, 0
        for act, pred in games:
            act_num += 1 if act.school_1_won else 0
            pred_num += pred
            den += 1
        row = {
            "bin_num": bin,
            "count": den,
            "actual": "UNK" if den == 0 else act_num / den,
            "predicted": "UNK" if den == 0 else pred_num / den,
        }
        df_rows.append(row)

    df = pd.DataFrame(data=df_rows)
    return tabulate(df, headers='keys')


def score_and_report(model: LogisticModel, years: List[Year]) -> None:
    history = _infer(model, years)
    print(_report_cross_entropy(history))
    print(_report_calibration(history))


def fit_and_score_and_report(featurizer: Featurizer, fit_years: List[Year], score_years: List[Year]) -> None:
    model = train_model(featurizer, fit_years)
    score_and_report(model, score_years)
