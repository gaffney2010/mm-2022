################################################################################
# Logging logic, must come first
SAFE_MODE = True
from tools.logger import configure_logging

import logging
configure_logging(SAFE_MODE, logging_level=logging.DEBUG)
################################################################################

from datetime import datetime
import sys
from typing import Dict, List

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


def get_reg_season_school(school_dict: Dict[str, School], school: School, year: Year) -> List[Game]:
    try:
        html = scraper_tools.read_url_to_string(SCHEDULE.format(school, year))
        df = pd.read_html(html)[-1]
        for req in ("Type", "Opponent", "Unnamed: 7", "Date"):
            if req not in df.columns:
                raise Exception("Bad df")
    except:
        _, _, exc_traceback = sys.exc_info()
        logger.log_error(f"Error opening school {school}", exc_traceback, stop_program=True)

    all_games = list()
    count_games = 0
    for _, row in df.iterrows():
        if row["Type"] != "REG":
            continue
        count_games += 1

        try:
            opponent = school_dict[row["Opponent"].split("\xa0")[0]]
        except:
            logger.log_error(f"Couldn't find key for school {row['Opponent']} found on school {school}", stop_program=False)
            continue

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



school_dict = get_schools(2021)
school = "west-virginia"
year = 2021
logging.debug(get_reg_season_school(school_dict, school, year))


logging.debug("GOODBYE")
