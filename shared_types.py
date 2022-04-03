from datetime import datetime
from typing import Any, Callable, Dict, Optional

import attr


School = str
Conf = Optional[str]
Year = int
# TODO: Replace type with sm.discrete.discrete_model.Logit
LogRegType = Any


class MmException(Exception):
    pass


class ScrapingException(Exception):
    pass


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

    def flip(self) -> "PlayoffGame":
        return PlayoffGame(
            year=self.year,
            school_1=self.school_2,
            school_1_seed=self.school_2_seed,
            school_2=self.school_1,
            school_2_seed=self.school_1_seed,
            school_1_won=not self.school_1_won,
        )


Featurizer = Callable[[PlayoffGame], Dict[str, float]]


@attr.s(frozen=True)
class LogisticModel(object):
    featurizer: Featurizer = attr.ib()
    model: LogRegType = attr.ib()
