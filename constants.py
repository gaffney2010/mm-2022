"""Some constants that will be shared potentially across files."""

import os

# If downloading, you need to set this directory to equal the directory that
#  houses this file.
from computer_constants import TOP_LEVEL_DIR

DATA_DIR = os.path.join(TOP_LEVEL_DIR, "data")
CSV_DIR = os.path.join(DATA_DIR, "csv")
LOGGING_DIR = os.path.join(TOP_LEVEL_DIR, "logging")
