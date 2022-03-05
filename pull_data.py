from tools import scraper_tools

FULL_YEAR = "https://www.sports-reference.com/cbb/seasons/{}-school-stats.html"

print("HELLO")

year = 2021
html = scraper_tools.read_url_to_string(FULL_YEAR.format(year))

print(html[:30])

print("GOODBYE")
