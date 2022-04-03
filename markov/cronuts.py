"""V1 experimental model described in README.  Codenamed cronuts.

As a V1 model, we'll do turn-over and score as the only actions.  With score-one (for fouls), score-two, and score-three as specific types of scores, with the assumption that the turn-over follows.  Notice that an offensive recovery after a missed one-and-one violates this assumption.  We build robustly enough that this is okay.  That is assumptions may be violated in training, but not in simulations.

This Graph would have a node, Play, with actions: turn-over, score-one, score-two, score-three.  The state considered for this node in the most simple model will be offense-only.

Note the convention established here that nodes are Pascal case and actions are hypenated.
"""

import random

import pandas as pd

from markov import markov
from tools import scraper_tools


class ParseError(Exception):
    pass


def score_diff(y: str, x: str) -> int:
    """I'm assuming that only teams in possession can score..."""
    # Return -1 ignores the row
    y_parse = y.split(" - ")
    if len(y_parse) != 2:
        return -1
    x_parse = x.split(" - ")
    if len(x_parse) != 2:
        return -1

    try:
        ya, yb = int(y_parse[0]), int(y_parse[1])
        xa, xb = int(x_parse[0]), int(x_parse[1])
    except:
        return -1

    a_fixed = ya == xa
    b_fixed = yb == xb

    if a_fixed:
        # Returns 0 here if y == x
        return yb - xb
    if b_fixed:
        return ya - xa

    # Neither fixed.
    # I'd like to understand this possibility better, so crash for now.
    raise ParseError(f"Weird score {y} and {x}")


def time_diff(y: str, x: str) -> markov.Second:
    y_parse = y.split(":")
    if len(y_parse) != 2:
        raise ParseError()
    x_parse = x.split(":")
    if len(x_parse) != 2:
        raise ParseError()

    try:
        y_min, y_sec = int(y_parse[0]), int(y_parse[1])
        x_min, x_sec = int(x_parse[0]), int(x_parse[1])
    except:
        raise ParseError()

    # -1 because clock counts down
    return -1 * (y_min * 60 + y_sec - x_min * 60 - x_sec)


url = "https://www.espn.com/mens-college-basketball/playbyplay/_/gameId/401408635"

html = scraper_tools.read_url_to_string(url)
html = html.replace(
    '<img class="team-logo" src="https://a.espncdn.com/combiner/i?img=/i/teamlogos/ncaa/500/150.png&amp;h=100&amp;w=100">',
    "duke",
).replace(
    '<img class="team-logo" src="https://a.espncdn.com/combiner/i?img=/i/teamlogos/ncaa/500/153.png&amp;h=100&amp;w=100">',
    "north-carolina",
)
dfs = pd.read_html(html)

for df_i in range(1, 3):
    half = dfs[df_i][["time", "team", "SCORE"]]

    new, time, score = True, None, None
    data = list()
    for i, row in half.iterrows():
        if new:
            time = row["time"]
            score = row["SCORE"]
            new = False
            print("New")
            continue

        # print(row)

        if i + 1 == len(half):
            # Because we have to look one-ahead
            break

        # We have to look one step ahead to know if this is a recordable move.
        # TODO: Handle this with a buffer to avoid the random-access.
        if row["team"] == half.iloc[i + 1]["team"]:
            # print("Maintain Possession")
            continue

        sd = score_diff(row["SCORE"], score)
        if sd == 0:
            action_id = "turn-over"
        elif sd == 1:
            action_id = "score-one"
        elif sd == 2:
            action_id = "score-two"
        elif sd == 3:
            action_id = "score-three"
        else:
            # Who knows why this happens.
            print("Malformed score")
            continue

        try:
            duration = time_diff(row["time"], time)
        except ParseError:
            # Malformed, who knows
            print("Malformed time")

        datum = markov.Datum(
            duration=duration,
            node_id="Play",
            state={"offense": row["team"]},
            action_id=action_id,
        )
        # print(datum)
        data.append(datum)

        # Update these
        time = row["time"]
        score = row["SCORE"]


def _flip_team(state: markov.State) -> None:
    if state["offense"] == "duke":
        state["offense"] = "north-carolina"
    elif state["offense"] == "north-carolina":
        state["offense"] = "duke"
    else:
        raise ParseError(f"Unexpected team encountered in: {state}")


def turn_over(state: markov.State) -> markov.NodeId:
    _flip_team(state)
    return "Play"


def score_one(state: markov.State) -> markov.NodeId:
    state["_scores"][state["offense"]] += 1
    _flip_team(state)
    return "Play"


def score_two(state: markov.State) -> markov.NodeId:
    state["_scores"][state["offense"]] += 2
    _flip_team(state)
    return "Play"


def score_three(state: markov.State) -> markov.NodeId:
    state["_scores"][state["offense"]] += 3
    _flip_team(state)
    return "Play"


def tip_off(state: markov.State) -> markov.NodeId:
    state["offense"] = "duke" if random.random() < 0.5 else "north-carolina"
    return "Play"


class SimpleLogger(markov.SimLogger):
    def __init__(self):
        self.pad = list()

    def append(self, s: str) -> None:
        self.pad.append(s)

    def dump(self) -> str:
        return "\n".join(self.pad)


graph = markov.Graph()
graph.add_node(
    "Play", ["offense"], ["turn-over", "score-one", "score-two", "score-three"]
)
graph.add_action("turn-over", turn_over)  # functions turn_over, etc. defined elsewhere
graph.add_action("score-one", score_one)
graph.add_action("score-two", score_two)
graph.add_action("score-three", score_three)
graph.add_action("tip-off", tip_off)

# graph.train(data)
# print(markov.sims(graph, teams=["duke", "north-carolina"]))
