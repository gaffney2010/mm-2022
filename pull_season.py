################################################################################
# Logging logic, must come first
SAFE_MODE = False
from tools.logger import configure_logging

import logging
configure_logging(screen=False, file=True, screen_level=logging.DEBUG, file_level=logging.WARNING)
################################################################################

from datetime import datetime
import functools
import sys
from typing import Dict, List, Set

import attr
from bs4 import BeautifulSoup
import dateutil
import pandas as pd

from tools import logger, scraper_tools


# TODO: Rename these.
FULL_YEAR = "https://www.sports-reference.com/cbb/seasons/{}-school-stats.html"
SCHEDULE = "https://www.sports-reference.com/cbb/schools/{}/{}-schedule.html"

School = str
Year = int


@attr.s(frozen=True)
class Game(object):
    winner: School = attr.ib()
    loser: School = attr.ib()
    date: datetime = attr.ib()


logging.debug("HELLO")


@functools.lru_cache(100)
def get_schools(year: Year) -> Dict[str, School]:
    # All schools in a given year mapped from representative string to the school
    html = scraper_tools.read_url_to_string(FULL_YEAR.format(year))
    soup = BeautifulSoup(html, features="lxml")
    raw_schools = soup.find_all("td", {"data-stat": "school_name"})
    schools = dict()
    for school in raw_schools:
        link = school.find("a")
        school_str = link.contents[0]
        school = link["href"].split("/")[3]
        schools[school_str] = school
    return schools


def get_reg_season_school(school: School, year: Year) -> List[Game]:
    try:
        html = scraper_tools.read_url_to_string(SCHEDULE.format(school, year))
        df = pd.read_html(html)[-1]
        for req in ("Type", "Opponent", "Unnamed: 7", "Date"):
            if req not in df.columns:
                raise Exception("Bad df")
    except:
        _, _, exc_traceback = sys.exc_info()
        logger.log_error(f"Error opening school {school}, skipped it", exc_traceback, stop_program=False)
        return []

    all_games = list()
    count_games = 0
    for _, row in df.iterrows():
        if row["Type"] != "REG":
            continue
        count_games += 1

        try:
            opponent = get_schools(year)[row["Opponent"].split("\xa0")[0]]
        except:
            logger.log_error(
                f"Couldn't find key for school {row['Opponent']} found on school {school}, continuing with non_key",
                stop_program=False
            )
            opponent = row["Opponent"].split("\xa0")[0].replace(" ", "-").upper()

        outcome = row["Unnamed: 7"]
        if outcome == "W":
            winner, loser = school, opponent
        elif outcome == "L":
            winner, loser = opponent, school
        else:
            # Unanticipated error
            logger.log_error(f"Unanticipated outcome: {row['Unnamed: 7']} found on school {school}", stop_program=False)

        date = dateutil.parser.parse(row["Date"])

        game = Game(winner=winner, loser=loser, date=date)
        all_games.append(game)

    if count_games < 20:
        # This seems like an error.
        logger.log_error(f"School {school} has fewer than 20 games.", stop_program=False)

    return all_games


def scrape_season(year: Year) -> Set[Game]:
    school_dict = get_schools(year)

    all_games = set()
    for _, school in school_dict.items():
        logging.debug(logger.log_section(_))
        logging.debug(_)
        for game in get_reg_season_school(school, year):
            all_games.add(game)

    return all_games


logging.warning(logger.log_section("New run for 2021"))
_ = scrape_season(2021)

logging.debug("GOODBYE")
