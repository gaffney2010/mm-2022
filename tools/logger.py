from datetime import datetime
import logging
import os

import traceback

from constants import *


class StoppingError(Exception):
    pass


def log_section(section_header: str) -> str:
    WIDTH = 30
    width = max(WIDTH, len(section_header)+4)
    left_margin = (width - len(section_header)) // 2
    right_margin = width - len(section_header) - left_margin

    fmt = list()
    fmt.append("\n")
    fmt.append("\n")
    fmt.append("=" * width)
    fmt.append("=" * left_margin + section_header.upper() + "=" * right_margin)
    fmt.append("=" * width)
    return "".join(fmt)


def log_error(
    error_msg: str,
    exc_traceback = None,
    stop_program: bool = True
) -> None:
    if stop_program:
        logging.error(error_msg)
    else:
        logging.warn(error_msg)
    if exc_traceback is not None:
        logging.error("Stack trace:")
        for l in traceback.format_tb(exc_traceback):
            logging.error(l)
    if stop_program:
        raise StoppingError


# TODO: Fix this so that both work at once, pls.  (https://stackoverflow.com/questions/13733552/logger-configuration-to-log-to-file-and-print-to-stdout)
def configure_logging(screen: bool = True, file: bool = False, screen_level=logging.INFO, file_level=logging.INFO) -> None:
    now = datetime.now()
    today = now.year * 10000 + now.month * 100 + now.day

    if screen:
        # Print to screen
        logging.basicConfig(
            format="%(asctime)s  %(levelname)s:\t%(module)s::%(funcName)s:%(lineno)d\t-\t%(message)s",
            level=screen_level,
        )
    if file:
        # Print to file
        logging.basicConfig(
            format="%(asctime)s  %(levelname)s:\t%(module)s::%(funcName)s:%(lineno)d\t-\t%(message)s",
            filename=os.path.join(LOGGING_DIR, str(today) + ".log"),
            level=file_level,
        )
