import functools
import logging
import sys
from typing import Dict, List, Set

from bs4 import BeautifulSoup
import dateutil
import pandas as pd

from tools import logger, scraper_tools
from shared_types import *


# TODO: Rename these.
FULL_YEAR = "https://www.sports-reference.com/cbb/seasons/{}-school-stats.html"
SCHEDULE = "https://www.sports-reference.com/cbb/schools/{}/{}-schedule.html"


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


def _school_field(raw: str) -> School:
    return raw.split("\xa0")[0]


def _open_school_page(school: School, year: Year, required_fields: List[str]) -> Optional[pd.DataFrame]:
    """Will report any errors for you, and return None"""
    try:
        html = scraper_tools.read_url_to_string(SCHEDULE.format(school, year))
        df = pd.read_html(html)[-1]
        for req in required_fields:
            if req not in df.columns:
                raise Exception("Bad df")
    except:
        # TODO: Check for a link on that cell.
        _, _, exc_traceback = sys.exc_info()
        logger.log_error(
            f"Error opening school {school}, skipped it",
            exc_traceback,
            stop_program=False,
        )
        return None
    return df[required_fields]


def get_conf_from_school_page(school: School, year: Year) -> Dict[School, Conf]:
    df = _open_school_page(school, year, ["Opponent", "Conf"])
    if df is None:
        return {}

    result = dict()
    for _, row in df.iterrows():
        if row["Conf"] == "" or row["Conf"] != row["Conf"]:
            continue
        result[_school_field(row["Opponent"])] = row["Conf"]

    return result


def get_reg_season_school(school: School, year: Year) -> List[Game]:
    df = _open_school_page(school, year, ["Type", "Opponent", "Unnamed: 7", "Date"])
    if df is None:
        return []

    all_games = list()
    count_games = 0
    for _, row in df.iterrows():
        if row["Type"] != "REG":
            continue
        count_games += 1

        try:
            opponent = get_schools(year)[_school_field(row["Opponent"])]
        except:
            logger.log_error(
                f"Couldn't find key for school {row['Opponent']} found on school {school}, continuing with non_key",
                stop_program=False,
            )
            opponent = _school_field(row["Opponent"]).replace(" ", "-").upper()

        outcome = row["Unnamed: 7"]
        if outcome == "W":
            winner, loser = school, opponent
        elif outcome == "L":
            winner, loser = opponent, school
        else:
            # Unanticipated error
            logger.log_error(
                f"Unanticipated outcome: {row['Unnamed: 7']} found on school {school}",
                stop_program=False,
            )

        date = dateutil.parser.parse(row["Date"])

        game = Game(winner=winner, loser=loser, date=date)
        all_games.append(game)

    if count_games < 10:
        # This seems like an error.
        logger.log_error(
            f"School {school} has fewer than 10 games.", stop_program=False
        )

    return all_games


@functools.lru_cache(100)
def get_conf(year: Year) -> Dict[School, Conf]:
    school_dict = get_schools(year)

    result = dict()
    for _, school in school_dict.items():
        logging.debug(logger.log_section(_))
        result.update(get_conf_from_school_page(school, year))

    return result


def scrape_season(year: Year) -> Set[Game]:
    school_dict = get_schools(year)

    all_games = set()
    for _, school in school_dict.items():
        logging.debug(logger.log_section(_))
        for game in get_reg_season_school(school, year):
            all_games.add(game)

    return all_games
