from datetime import datetime
from typing import Any, Callable, Dict

import attr


School = str
Year = int


@attr.s(frozen=True)
class Game(object):
    winner: School = attr.ib()
    loser: School = attr.ib()
    date: datetime = attr.ib()


@attr.s(frozen=True)
class PlayoffGame(object):
    year: Year = attr.ib()
    school_1: School = attr.ib()
    school_1_seed: int = attr.ib()
    school_2: School = attr.ib()
    school_2_seed: int = attr.ib()
    school_1_won: bool = attr.ib()


Featurizer = Callable[[PlayoffGame], Dict[str, float]]


@attr.s(frozen=True)
class LogisticModel(object):
    featurizer: Featurizer = attr.ib()
    # TODO: Replace type with sm.discrete.discrete_model.Logit
    model: Any = attr.ib()
