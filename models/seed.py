from typing import Dict

from shared_types import *


def seed_featurizer(game: PlayoffGame) -> Dict[str, float]:
    return {f"{i}_seed": 1 if game.school_1_seed == i else 0 for i in range(1, 17)}
