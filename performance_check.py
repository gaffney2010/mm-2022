"""Checks how often random guesses reach given performance."""

import random
from typing import List

import pandas as pd
import tqdm

from tools import odds_lib, file_lib


def shuffle(sizes: List[float]) -> List[float]:
    """First shuffle games, then which side."""
    num_games = len(sizes) // 2
    game_order = list(range(num_games))
    random.shuffle(game_order)
    flips = [random.randint(0, 1) for _ in range(num_games)]

    result = list()
    for i in range(num_games):
        a = game_order[i] + flips[i]
        b = game_order[i] + 1 - flips[i]
        result.append(sizes[a])
        result.append(sizes[b])

    return result


def score_sizes(bets: pd.DataFrame, sizes: List[float]) -> float:
    wallet = 0.0
    for i, row in bets.iterrows():
        odds, bet_size = row["money_line"], sizes[i]
        lay = odds_lib.lay_from_odds(odds) * bet_size
        if row["won"]:
            wallet += lay * odds_lib.win_multiplier(odds)
        else:
            wallet -= lay
    return wallet


def sims(bets: pd.DataFrame, actual: float, num_sims: int = 5000) -> float:
    num, den = 0, 0
    for _ in tqdm.tqdm(range(num_sims)):
        sizes = list(bets["bet_size"])
        res = score_sizes(bets, shuffle(sizes))
        if res > actual:
            num += 1
        den += 1
    return num / den


bets = file_lib.read_csv("2022_bets")
sizes = list(bets["bet_size"])
actual = score_sizes(bets, sizes)
print(sims(bets, actual))
