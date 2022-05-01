"""Uses 2020 full-year data"""

# TODO: Better importing
from top_level_dir import top_level_dir
import sys
sys.path.append(top_level_dir)

import json
import os
import pickle
from typing import Tuple

import argparse
import numpy as np

from computer_constants import *
from constants import *
from models import bradley_terry
from shared_types import *


parser = argparse.ArgumentParser()
parser.add_argument("away")
parser.add_argument("home")
parser.add_argument("date", type=int)
args = vars(parser.parse_args())

# TODO: Assert that date > 2019-2020 season


# Translates teams from passed format to the local format.
with open(JUPES_TO_MM_JSON, "r") as f:
    jupes_to_mm = json.loads(f.read())

away_team = jupes_to_mm[args["away"]]
home_team = jupes_to_mm[args["home"]]

# Not actually a playoff game - think of this like a bad now.
game = PlayoffGame(year=2020, school_1=away_team, school_2=home_team)

prob_away_team_won = bradley_terry.bt(game, with_hd_save=True)

result = {"prob_away_win": prob_away_team_won, "prob_home_win": 1.0 - prob_away_team_won}
print(json.dumps(result))
