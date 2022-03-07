import networkx as nx

from pull_scripts import pull_season


G = nx.DiGraph()

year = 2021
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
pr_sorted = sorted([(v, k) for k, v in pr.items()])
print(pr_sorted)
