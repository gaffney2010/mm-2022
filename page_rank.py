from typing import Dict

import networkx as nx

from pull_scripts import pull_season
from shared_types import *


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


pr_sorted = sorted([(v, k) for k, v in page_ranks(2021).items()])
print(pr_sorted)
