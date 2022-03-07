################################################################################
# Logging logic, must come first
from tools.logger import configure_logging
import logging

configure_logging(
    screen=False, file=True, screen_level=logging.DEBUG, file_level=logging.WARNING
)
################################################################################

from models import bradley_terry, model, page_rank, random_bench, seed

# print("")
# print("RANDOM BENCHMARK")
# print(model.report(random_bench.history([2019, 2021])))


# print("")
# print("SEED MODEL")
# seed_model = seed.train_model(list(range(2017, 1985, -1)))
# history = seed.infer(seed_model, [2021, 2019, 2018])
# print(model.report(history))


# print("")
# print("BRADLEY-TERRY")
# print(model.report(bradley_terry.history([2019, 2021])))


print("")
print("PAGE RANK LOESS")
print(model.report(page_rank.history([2019, 2021])))
