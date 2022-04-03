"""V1 experimental model described in README.  Codenamed cronuts.

As a V1 model, we'll do turn-over and score as the only actions.  With score-one (for fouls), score-two, and score-three as specific types of scores, with the assumption that the turn-over follows.  Notice that an offensive recovery after a missed one-and-one violates this assumption.  We build robustly enough that this is okay.  That is assumptions may be violated in training, but not in simulations.

This Graph would have a node, Play, with actions: turn-over, score-one, score-two, score-three.  The state considered for this node in the most simple model will be offense-only.

Note the convention established here that nodes are Pascal case and actions are hypenated.
"""

from tools import scraper_tools

url = "https://www.espn.com/mens-college-basketball/playbyplay/_/gameId/401408635"

html = scraper_tools.read_url_to_string(url)
print(html)
