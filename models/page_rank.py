import functools
from typing import Dict, List, Tuple

import networkx as nx

from pull_scripts import pull_round_1, pull_season
from shared_types import *


@functools.lru_cache(100)
def page_ranks(year: Year) -> Dict[School, float]:
    G = nx.DiGraph()

    nodes = set()
    for game in pull_season.scrape_season(year):
        if game.winner not in nodes:
            nodes.add(game.winner)
            G.add_node(game.winner)
        if game.loser not in nodes:
            nodes.add(game.loser)
            G.add_node(game.loser)
        G.add_edge(game.loser, game.winner)

    pr = nx.pagerank(G)
    return pr


@functools.lru_cache(100)
def pr_ranks(year: Year) -> Dict[School, float]:
    pr = page_ranks(year)
    pr = sorted([(-v, k) for k, v in pr.items()])
    pr = {xi[1]: i + 1 for i, xi in enumerate(pr)}
    return pr


# Returns scatter plot of page-rank diffence by win/loss
@functools.lru_cache(100)
def experience(years: Tuple[Year]) -> List[Tuple[float, float]]:
    result = list()
    for year in years:
        pr = pr_ranks(year)
        for game in pull_season.scrape_season(year):
            result.append((pr[game.winner] - pr[game.loser], 1.0))
            result.append((pr[game.loser] - pr[game.winner], 0.0))

    return sorted(result)


# For smoothing
def weight(x: float, y: float, bandwidth: float) -> float:
    a = abs(x - y)
    if a > bandwidth:
        return 0
    return 1 - a / bandwidth


BANDWIDTH = 50


def infer(game: PlayoffGame, loess_years: Tuple[Year]) -> float:
    pr = pr_ranks(game.year)
    diff = pr[game.school_1] - pr[game.school_2]

    num, den = 0, 0
    bandwidth = BANDWIDTH
    for x, y in experience(loess_years):
        w = weight(diff, x, bandwidth)
        num += w * y
        den += w

    result = num / den
    if result > 0.95:
        result = 0.95
    if result < 0.05:
        result = 0.05
    return result


def history(years: List[Year], loess_years: Tuple[Year]) -> Dict[PlayoffGame, float]:
    result = dict()
    for year in years:
        for game in pull_round_1.read_playoffs(year):
            result[game] = infer(game, loess_years)
    return result
