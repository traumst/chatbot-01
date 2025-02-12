import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename='server.log',
    level=logging.DEBUG)
logger.warning("Logging enabled with level %s", logger.level)