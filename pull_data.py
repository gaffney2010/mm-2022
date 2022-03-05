from typing import List

from bs4 import BeautifulSoup

from tools import scraper_tools


FULL_YEAR = "https://www.sports-reference.com/cbb/seasons/{}-school-stats.html"
School = int


print("HELLO")

def get_schools(year: int) -> List[School]:
    html = scraper_tools.read_url_to_string(FULL_YEAR.format(year))
    soup = BeautifulSoup(html, features="lxml")
    raw_schools = soup.find_all("td", {"data-stat": "school_name"})
    schools = list()
    for school in raw_schools:
        link = school.find("a")["href"]
        school = link.split("/")[3]
        schools.append(school)
    return schools

print(get_schools(2021))

print("GOODBYE")
