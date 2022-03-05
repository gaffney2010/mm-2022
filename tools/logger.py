from datetime import datetime
import logging
import os

import traceback

from constants import *


class StoppingError(Exception):
    pass


def log_section(section_header: str) -> None:
    WIDTH = 30
    width = max(WIDTH, len(section_header)+4)
    left_margin = (width - len(section_header)) // 2
    right_margin = width - len(section_header) - left_margin

    logging.info("\n")
    logging.info("\n")
    logging.info("=" * width)
    logging.info("=" * left_margin + section_header.upper() + "=" * right_margin)
    logging.info("=" * width)


def log_error(
    error_msg: str,
    exc_traceback = None,
    stop_program: bool = True
) -> None:
    logging.error(error_msg)
    if exc_traceback is not None:
        logging.error("Stack trace:")
        for l in traceback.format_tb(exc_traceback):
            logging.error(l)
    if stop_program:
        raise StoppingError


def configure_logging(safe_mode: bool, logging_level = logging.INFO) -> None:
    now = datetime.now()
    today = now.year * 10000 + now.month * 100 + now.day

    if safe_mode:
        # Print to screen
        logging.basicConfig(
            format="%(asctime)s  %(levelname)s:\t%(module)s::%(funcName)s:%(lineno)d\t-\t%(message)s",
            level=logging_level,
        )
    else:
        # Print to file
        logging.basicConfig(
            format="%(asctime)s  %(levelname)s:\t%(module)s::%(funcName)s:%(lineno)d\t-\t%(message)s",
            filename=os.path.join(LOGGING_DIR, str(today) + ".log"),
            level=logging_level,
        )
