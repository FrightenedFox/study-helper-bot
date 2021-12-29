import logging

from studyhelperbot import config


def initialize_logging():
    params = config("logging")

    log_formatter = logging.Formatter(
        "%(asctime)s [%(threadName)-12.12s] [%(filename)-20.20s] [%(funcName)-30.30s]"
        "[l %(lineno)-4.4s] [%(levelname)-7.7s]\t%(message)s"
    )
    root_logger = logging.getLogger()

    file_handler = logging.FileHandler(f"{params['log_path']}/{params['log_filename']}.log")
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)

    root_logger.setLevel(getattr(logging, params["level"]))
