################################################################################
# Logging logic, must come first
from tools.logger import configure_logging

import logging

configure_logging(
    screen=True, file=False, screen_level=logging.DEBUG, file_level=logging.WARNING
)
################################################################################

import collections
import hashlib
import random
import sys
from typing import List

from bs4 import BeautifulSoup

from tools import logger, scraper_tools
from shared_types import *


POST_SEASON = "https://www.sports-reference.com/cbb/postseason/{}-ncaa.html"


def read_quadrant(html: str, year: Year, seeds_found) -> List[PlayoffGame]:
    result = list()
    for i, game in enumerate(html.split("<!-- game -->")):
        # Before any tag there is no game.
        if i == 0:
            continue

        school_split = game.split("<!-- team -->")
        if len(school_split) != 3:
            # We've reached the of this quadrant
            break

        try:
            school_1_seed = int(school_split[1].split("<span>")[1].split("</span>")[0])
            school_2_seed = int(school_split[2].split("<span>")[1].split("</span>")[0])
        except:
            _, _, exc_traceback = sys.exc_info()
            logger.log_error(
                f"Malformed playoff game: {game}", exc_traceback, stop_program=False
            )

        if school_1_seed + school_2_seed != 17:
            # Not first round
            continue

        seeds_found[school_1_seed] += 1
        seeds_found[school_2_seed] += 1

        school_1_won = school_split[0].find("winner") != -1
        school_2_won = school_split[1].find("winner") != -1
        if not (school_1_won ^ school_2_won):
            if (
                hashlib.sha224(game.encode()).hexdigest()
                == "230081c2419c0304f6c4fa2ef6067b385ced1ea5f38968f1eeace101"
            ):
                # Known exception: Oregon / VCU forfeit
                continue
            # TODO: Better exceptions
            raise Exception

        try:
            soup_1 = BeautifulSoup(school_split[1], features="lxml")
            link_1 = soup_1.find("a")
            school_1 = link_1["href"].split("/")[3]
        except:
            _, _, exc_traceback = sys.exc_info()
            logger.log_error(
                f"Malformed playoff game: {game}", exc_traceback, stop_program=False
            )

        try:
            soup_2 = BeautifulSoup(school_split[2], features="lxml")
            link_2 = soup_2.find("a")
            school_2 = link_2["href"].split("/")[3]
        except:
            _, _, exc_traceback = sys.exc_info()
            logger.log_error(
                f"Malformed playoff game: {game}", exc_traceback, stop_program=False
            )

        game = PlayoffGame(
            year=year,
            school_1=school_1,
            school_1_seed=school_1_seed,
            school_2=school_2,
            school_2_seed=school_2_seed,
            school_1_won=school_1_won,
        )
        if random.random() > 0.5:
            game = game.flip()
            # TODO: Fix this nonsense
            result.append(game)
        else:
            result.append(game)

    return result


def read_playoffs(year: Year) -> List[PlayoffGame]:
    random.seed(year)

    seeds_found = collections.defaultdict(int)

    html = scraper_tools.read_url_to_string(POST_SEASON.format(year))
    soup = BeautifulSoup(html, features="lxml")

    result = list()
    # Each of 4 divisions start with <div id="bracket" class="team16">
    for div in soup.find_all("div", {"id": "bracket", "class": "team16"}):
        result += read_quadrant(str(div), year, seeds_found)

    for k in range(1, 17):
        if k not in seeds_found or seeds_found[k] != 4:
            logger.log_error(
                f"Missing playoff games for year {year}, found these seeds: {seeds_found}",
                stop_program=True,
            )

    return result
