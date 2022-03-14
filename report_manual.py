################################################################################
# Logging logic, must come first
from tools.logger import configure_logging
import logging

configure_logging(
    screen=False, file=True, screen_level=logging.DEBUG, file_level=logging.WARNING
)
################################################################################

from typing import Any, Dict

import pandas as pd

from models import bradley_terry, page_rank, seed
from shared_types import *


raw_games = [
    {'school_1': 'gonzaga', 'school_1_seed': 1, 'school_2': 'georgia-state', 'school_2_seed': 16},
    {'school_1': 'boise-state', 'school_1_seed': 8, 'school_2': 'memphis', 'school_2_seed': 9},
    {'school_1': 'connecticut', 'school_1_seed': 5, 'school_2': 'new-mexico-state', 'school_2_seed': 12},
    {'school_1': 'arkansas', 'school_1_seed': 4, 'school_2': 'vermont', 'school_2_seed': 13},
    {'school_1': 'texas-tech', 'school_1_seed': 3, 'school_2': 'montana-state', 'school_2_seed': 14},
    {'school_1': 'michigan-state', 'school_1_seed': 7, 'school_2': 'davidson', 'school_2_seed': 10},
    {'school_1': 'duke', 'school_1_seed': 2, 'school_2': 'cal-state-fullerton', 'school_2_seed': 15},
    {'school_1': 'baylor', 'school_1_seed': 1, 'school_2': 'norfolk-state', 'school_2_seed': 16},
    {'school_1': 'north-carolina', 'school_1_seed': 8, 'school_2': 'marquette', 'school_2_seed': 9},
    {'school_1': 'ucla', 'school_1_seed': 4, 'school_2': 'akron', 'school_2_seed': 13},
    {'school_1': 'texas', 'school_1_seed': 6, 'school_2': 'virginia-tech', 'school_2_seed': 11},
    {'school_1': 'purdue', 'school_1_seed': 3, 'school_2': 'yale', 'school_2_seed': 14},
    {'school_1': 'murray-state', 'school_1_seed': 7, 'school_2': 'san-francisco', 'school_2_seed': 10},
    {'school_1': 'kentucky', 'school_1_seed': 2, 'school_2': 'saint-peters', 'school_2_seed': 15},
    {'school_1': 'seton-hall', 'school_1_seed': 8, 'school_2': 'texas-christian', 'school_2_seed': 9},
    {'school_1': 'houston', 'school_1_seed': 5, 'school_2': 'alabama-birmingham', 'school_2_seed': 12},
    {'school_1': 'illinois', 'school_1_seed': 4, 'school_2': 'chattanooga', 'school_2_seed': 13},
    {'school_1': 'colorado-state', 'school_1_seed': 6, 'school_2': 'michigan', 'school_2_seed': 11},
    {'school_1': 'tennessee', 'school_1_seed': 3, 'school_2': 'longwood', 'school_2_seed': 14},
    {'school_1': 'ohio-state', 'school_1_seed': 7, 'school_2': 'loyola-il', 'school_2_seed': 10},
    {'school_1': 'villanova', 'school_1_seed': 2, 'school_2': 'delaware', 'school_2_seed': 15},
    {'school_1': 'san-diego-state', 'school_1_seed': 8, 'school_2': 'creighton', 'school_2_seed': 9},
    {'school_1': 'iowa', 'school_1_seed': 5, 'school_2': 'richmond', 'school_2_seed': 12},
    {'school_1': 'providence', 'school_1_seed': 4, 'school_2': 'south-dakota-state', 'school_2_seed': 13},
    {'school_1': 'louisiana-state', 'school_1_seed': 6, 'school_2': 'iowa-state', 'school_2_seed': 11},
    {'school_1': 'wisconsin', 'school_1_seed': 3, 'school_2': 'colgate', 'school_2_seed': 14},
    {'school_1': 'southern-california', 'school_1_seed': 7, 'school_2': 'miami-fl', 'school_2_seed': 10},
    {'school_1': 'auburn', 'school_1_seed': 2, 'school_2': 'jacksonville', 'school_2_seed': 15},
]

games = list()
for raw_game in raw_games:
    game = PlayoffGame(
        year=2022,
        school_1=raw_game["school_1"],
        school_1_seed=raw_game["school_1_seed"],
        school_2=raw_game["school_2"],
        school_2_seed=raw_game["school_2_seed"],
        school_1_won=None,  # Don't use this
    ) 
    games.append(game)


seed_model = seed.train_model(list(range(1985, 2020)) + [2021])


# TODO: Share with the other file, I guess.
def row_from_game(game: PlayoffGame) -> Dict[str, Any]:
    return {
        "school": game.school_1,
        "opponent": game.school_2,
        "seed": game.school_1_seed,
        "seed_prob": seed._infer_single_game(seed_model, game),
        "bt": bradley_terry.bt(game),
        # "pr": page_rank.page_ranks(game.year)[game.school_1],
        "pr": page_rank.pr_ranks(game.year)[game.school_1],
        "pr_prob": page_rank.infer(game, loess_years=(2022, 2021, 2020, 2019, 2018)),
        "won": game.school_1_won,
    }


year = 2022

data = list()
for game in games:
    data.append(row_from_game(game))
    data.append(row_from_game(game.flip()))

df = pd.DataFrame(data)

df.to_csv(f"{year}.csv")
