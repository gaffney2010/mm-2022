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
from tools import file


raw_games = file.read_csv("manual_input_2022")

games = list()
for _, raw_game in raw_games.iterrows():
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
file.write_csv(df, year)
