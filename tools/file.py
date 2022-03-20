import os

import pandas as pd

from constants import *


def write_csv(df: pd.DataFrame, name: str) -> None:
    df.to_csv(os.path.join(CSV_DIR, f"{name}.csv"))


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(os.path.join(CSV_DIR, f"{name}.csv"))
