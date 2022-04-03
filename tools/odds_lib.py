import numpy as np


def lay_from_odds(odds: int) -> float:
    d = abs(odds) / 100
    d = np.sqrt(d)
    if odds > 0:
        return 1.0 / d
    return d


def prob_from_odds(odds: int) -> float:
    """Assumes even-money"""
    d = abs(odds) / 1000
    if odds > 0:
        return 1 / (1 + d)
    return d / (1 + d)


def win_multiplier(odds: int) -> float:
    d = abs(odds) / 100
    if odds > 0:
        return d
    return 1 / d
