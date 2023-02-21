import logging

GREY = "\x1b[90;20m"
YELLOW = "\x1b[33;20m"
RED = "\x1b[31;20m"
BOLD_RED = "\x1b[31;1m"
RESET = "\x1b[0m"

FORMAT = "[%(asctime)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"

FORMATS = {
    logging.DEBUG: GREY + FORMAT + RESET,
    logging.INFO: FORMAT,
    logging.WARNING: YELLOW + FORMAT + RESET,
    logging.ERROR: RED + FORMAT + RESET,
    logging.CRITICAL: BOLD_RED + FORMAT + RESET,
}


# https://stackoverflow.com/a/56944256
class CustomFormatter(logging.Formatter):
    def format(self, record):
        log_fmt = FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger(name: str):
    logger = logging.getLogger(name)

    logger.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    ch.setFormatter(CustomFormatter())

    logger.addHandler(ch)

    return logger
