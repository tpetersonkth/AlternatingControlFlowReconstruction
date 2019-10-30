import logging

logging.basicConfig(format="%(message)s")
formatter = logging.Formatter('%(message)s')
syslog = logging.StreamHandler()
syslog.setFormatter(formatter)
logger = logging.getLogger("")
logger.handlers = []
logger.addHandler(syslog)
logger.setLevel('INFO')