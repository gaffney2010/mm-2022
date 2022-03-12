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


seed_model = seed.train_model(list(range(1985, 2020)) + [2021])

def row_from_game(game: PlayoffGame) -> Dict[str, Any]:
    return {
        "school": game.school_1,
        "opponent": game.school_2,
        "seed": game.school_1_seed,
        "seed_prob": seed._infer_single_game(seed_model, game),
        "bt": bradley_terry.bt(game),
        # "pr": page_rank.page_ranks(game.year)[game.school_1],
        "pr": page_rank.pr_ranks(game.year)[game.school_1],
        "pr_prob": page_rank.infer(game),
        "won": game.school_1_won
    }

year = 2021

data = list()
for game in pull_round_1.read_playoffs(year):
    data.append(row_from_game(game))
    data.append(row_from_game(game.flip()))

df = pd.DataFrame(data)

df.to_csv(f"{year}.csv")
