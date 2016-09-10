from settings import settings

import logging


class TextClassifier:
    def __init__(self):
        self.config = settings()

        self.logger = logging.getLogger('BotLogger.NLP')
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(self.config.log)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
