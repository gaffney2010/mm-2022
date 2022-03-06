import logging
from typing import Dict, List

from shared_types import *


def train_model(featurizer: Featurizer, years: List[Year]) -> LogisticModel:
    raise NotImplementedError


def _infer(model: LogisticModel, years: List[Year]) -> Dict[PlayoffGame, float]:
    raise NotImplementedError


def _report_cross_entropy(history: Dict[PlayoffGame, float]) -> str:
    raise NotImplementedError


def _report_calibration(history: Dict[PlayoffGame, float], bins: int = 5) -> str:
    raise NotImplementedError


def score_and_report(model: LogisticModel, years: List[Year]) -> None:
    history = _infer(model, years)
    logging.info(_report_cross_entropy(history))
    logging.info(_report_calibration(history))
