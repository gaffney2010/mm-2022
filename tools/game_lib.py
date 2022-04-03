"""Shared game transformations."""

from typing import Any, Dict

from models import bradley_terry, page_rank, seed
from shared_types import *


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
        "pr_prob": page_rank.infer(game, loess_years=(2022, 2021, 2020, 2019, 2018)),
        "won": game.school_1_won,
    }
