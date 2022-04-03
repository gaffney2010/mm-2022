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
from pull_scripts import pull_round_1
from shared_types import PlayoffGame
from tools import file_lib, game_lib


year = 2021

data = list()
for game in pull_round_1.read_playoffs(year):
    data.append(game_lib.row_from_game(game))
    data.append(game_lib.row_from_game(game.flip()))

df = pd.DataFrame(data)
file_lib.write_csv(df, year)
