################################################################################
# Logging logic, must come first
from tools.logger import configure_logging

import logging

configure_logging(
    screen=False, file=True, screen_level=logging.DEBUG, file_level=logging.WARNING
)
################################################################################

from models import model, seed


model.fit_and_score_and_report(
    seed.seed_featurizer,
    fit_years=list(range(2017, 1985, -1)),
    score_years=[2021, 2019, 2018],
)
