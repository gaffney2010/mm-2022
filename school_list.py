from pull_scripts import pull_season

for k, v in pull_season.get_schools(2022).items():
    print(f"{k},{v}")
