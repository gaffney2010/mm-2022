"""This file helps tune the unit bet size, to manage probability of bankrupcy."""

import random

import pandas as pd

from tools import file_lib, odds_lib


def one_sim_bankrupcy(bets: pd.DataFrame, bankroll: float, unit: float) -> bool:
    wallet = bankroll
    for bet in bets:
        odds, bet_size = bet["money_line"], bet["bet_size"]
        lay = odds_lib.lay_from_odds(odds) * bet_size * unit
        if random.random() < odds_lib.prob_from_odds(odds):
            # Win
            wallet += lay * odds_lib.win_multiplier(odds)
        else:
            # Lose
            wallet -= lay
        if wallet < 0:
            return True
    return False


def prob_bankrupcy(
    bets: pd.DataFrame, bankroll: float, unit: float, no_sims: int
) -> float:
    num, den = 0, 0
    for _ in range(no_sims):
        den += 1
        if one_sim_bankrupcy(bets, bankroll, unit):
            num += 1
    return num / den


def find_unit(
    bets: pd.DataFrame,
    bankroll: float,
    target_prob_bankrupcy: float,
    no_sims: int = 10000,
    eps: float = 0.001,
) -> float:
    min, max = 0, bankroll
    mid_p = 1.0
    while abs(mid_p - target_prob_bankrupcy) > eps:
        mid = (min + max) / 2.0
        mid_p = prob_bankrupcy(bets, bankroll, mid, no_sims)
        print(f"{mid} => {mid_p}")
        if target_prob_bankrupcy < mid_p:
            max = mid
        else:
            min = mid
    return mid


bets = file_lib.read_csv("2022_bets")
print(find_unit(bets, 1000, 0.1, eps=0.01))
