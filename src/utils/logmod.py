import logging

from rich.logging import RichHandler


def init(level: int) -> None:
    assert level is not logging.NOTSET
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(asctime)s @%(name)s: %(message)s",
        datefmt="[%Y-%m-%dT%H:%M:%S]",
        handlers=[
            RichHandler(show_time=False, show_level=False, show_path=False)
            # logging.FileHandler(f"general.log"),
            # logging.StreamHandler(sys.stdout),
        ])

def log_level_atoi(log_level: str) -> int:
    match log_level.lower():
        case "none":
            raise ValueError(f"Log is disabled with logging.NOTSET {logging.NOTSET}")
        case "debug":
            return logging.DEBUG
        case "info":
            return logging.INFO
        case "warn":
            return logging.WARNING
        case "error":
            return logging.ERROR
        case "fatal":
            return logging.CRITICAL
        case _:
            raise ValueError(f"Unknown log level [{log_level}]")

def log_level_itoa(log_level: int) -> str:
    match log_level:
        case logging.DEBUG:
            return "debug"
        case logging.INFO:
            return "info"
        case logging.WARNING:
            return "warn"
        case logging.ERROR:
            return "error"
        case logging.CRITICAL:
            return "fatal"
        case _:
            raise ValueError(f"Unknown log level [{log_level}]")