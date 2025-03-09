import logging
import os

log_level_dict = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARN": logging.WARNING,
    "ERROR": logging.ERROR
}

log_level = log_level_dict[str(os.getenv("LOG_LEVEL", "DEBUG")).upper()]


def get_logger(name):
    """
    :param log_level
    :param name: The name of the logger to be created.
    :return: A logger instance configured with a specific format and stream handler.
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.propagate = False

    ch = logging.StreamHandler()
    ch.setLevel(log_level)

    ch.setFormatter(CustomFormatter())

    logger.addHandler(ch)
    return logger


class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
