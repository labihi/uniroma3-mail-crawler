import coloredlogs
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO")
coloredlogs.install(level='INFO', logger=logger, fmt='%(message)s')
