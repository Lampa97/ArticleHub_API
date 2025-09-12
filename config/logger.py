import logging


def get_logger(log_file: str):
    logger = logging.getLogger(log_file)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_file, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def write_log(log_line, log_file="logs/general_logs.log"):
    logger = get_logger(log_file)
    logger.info(log_line)
