import collections
from typing import Dict, List

import pandas as pd
from tabulate import tabulate

from pull_scripts import pull_round_1
from shared_types import *


# TODO: This isn't actually cross entropy
def _report_cross_entropy(history: Dict[PlayoffGame, float]) -> str:
    num, den = 0, 0
    for act, pred in history.items():
        num += 1 - pred if act.school_1_won else pred
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
    return tabulate(df, headers="keys")


def report(history: Dict[PlayoffGame, float]) -> str:
    return "\n".join([
        _report_cross_entropy(history),
        _report_calibration(history),
    ])
