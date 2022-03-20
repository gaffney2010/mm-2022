import numpy as np


def _odds_str(odds: int) -> str:
    # TODO: Probably should just update these.
    # For backwards compatibility with historical functions
    if odds > 0:
        return f"+{odds}"
    return str(odds)


def lay_from_odds(odds: int) -> float:
    odds = _odds_str(odds)
    d = int(odds[1:]) / 100
    d = np.sqrt(d)
    if odds[0] == "+":
        return 1.0 / d
    return d


def prob_from_odds(odds: int) -> float:
    """Assumes even-money"""
    odds = _odds_str(odds)
    d = int(odds[1:]) / 100
    if odds[0] == "+":
        return 1 / (1 + d)
    return d / (1 + d)


def win_multiplier(odds: int) -> float:
    odds = _odds_str(odds)
    d = int(odds[1:]) / 100
    if odds[0] == "+":
        return d
    return 1 / d
