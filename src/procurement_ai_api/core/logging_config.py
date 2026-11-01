
import logging
import colorlog


def setup_logging(level=logging.INFO):
    handler = colorlog.StreamHandler()

    handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid adding duplicate handlers
    if not any(
        isinstance(h, colorlog.StreamHandler)
        for h in root_logger.handlers
    ):
        root_logger.addHandler(handler)
