import logging


class SimpleColorFormatter(logging.Formatter):
    COLORS = {
        logging.INFO: "\033[92m",
        logging.WARNING: "\033[93m",
        logging.ERROR: "\033[91m",
    }
    RESET = "\033[0m"

    def format(self, record):
        original_level = record.levelname
        color = self.COLORS.get(record.levelno)

        if color:
            record.levelname = f"{color}{original_level}{self.RESET}"

        message = super().format(record)
        record.levelname = original_level
        return message


def setup_logging():
    handler = logging.StreamHandler()

    formatter = SimpleColorFormatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    )

    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)