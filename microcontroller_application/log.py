"""
Logging infrastructure for the microcontroller application
"""

from datetime import datetime, timezone
from pathlib import Path
from sys import stdout

import logging
from time import gmtime


MAX_TRIMMED_PATH_LENGTH = 100

NOTHING_SPECIAL = ""

GREY = "\x1b[90;20m"
YELLOW = "\x1b[33;20m"
RED = "\x1b[31;20m"
BOLD_RED = "\x1b[31;1m"
RESET = "\x1b[0m"

BASE_FORMAT = f"[%(fmttime)s] {{color_start}}%(levelname)-8s{{color_end}} %(pathline)s\n{{color_start}}%(message)s{{color_end}}"

FORMATS = {
    logging.DEBUG: BASE_FORMAT.format(color_start=GREY, color_end=RESET),
    logging.INFO: BASE_FORMAT.format(
        color_start=NOTHING_SPECIAL, color_end=NOTHING_SPECIAL
    ),
    logging.WARNING: BASE_FORMAT.format(color_start=YELLOW, color_end=RESET),
    logging.ERROR: BASE_FORMAT.format(color_start=RED, color_end=RESET),
    logging.CRITICAL: BASE_FORMAT.format(color_start=BOLD_RED, color_end=RESET),
}


CWD = Path.cwd()


# https://stackoverflow.com/a/56944256
class CustomFormatter(logging.Formatter):
    def format(self, record):
        dt = datetime.fromtimestamp(record.created)
        dt_utc = dt.astimezone(timezone.utc)

        record.fmttime = dt_utc.strftime("%Y-%m-%d %H:%M:%S.%f %Z")

        shortened_path = Path(record.pathname).relative_to(CWD)

        path_line = f"{shortened_path}:{record.lineno}"
        record.pathline = path_line

        log_fmt = FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        formatter.converter = gmtime
        return formatter.format(record)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # https://stackoverflow.com/a/44426266
    logger.propagate = False

    stdout_handler = logging.StreamHandler(stdout)
    stdout_handler.setFormatter(CustomFormatter())
    logger.addHandler(stdout_handler)

    return logger
