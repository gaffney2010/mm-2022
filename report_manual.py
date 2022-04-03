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
from tools import file_lib, game_lib


raw_games = file_lib.read_csv("manual_input_2022")

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


year = 2022

data = list()
for game in games:
    data.append(game_lib.row_from_game(game))
    data.append(game_lib.row_from_game(game.flip()))

df = pd.DataFrame(data)
file_lib.write_csv(df, year)
