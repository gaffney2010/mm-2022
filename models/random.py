# This is for benchmarking
import random
from typing import Dict, List

from pull_scripts import pull_round_1
from shared_types import *


def history(years: List[Year]) -> Dict[PlayoffGame, float]:
    result = dict()
    for year in years:
        for game in pull_round_1.read_playoffs(year):
            result[game] = random.random()
    return result
