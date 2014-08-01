import logging

def make_logger():
    """
    Setup logging.
    """
    logger = logging.getLogger("pyconfd")
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)

    logger.addHandler(ch)
    return logger

log = make_logger()
