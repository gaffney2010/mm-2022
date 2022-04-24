from pull_scripts import pull_season


result = list()
result.append("team_1,team_2,yyyymmdd")
for game in pull_season.scrape_season(2021):
    result.append(",".join([game.winner, game.loser, game.date.strftime("%Y%m%d")]))

with open("2021.csv", "w") as f:
    for line in result:
        f.write(line + "\n")
