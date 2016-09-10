from settings import settings
import logging

__author__ = 'g.lavrentyeva'

class User:
    def __init__(self):
        self.config = settings()

        self.logger = logging.getLogger('BotLogger.User')
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(self.config.log)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        self.statistics = 0
        self.superuser = False
        self.teacher = False
        self.logger.info('Init done')
        self.isBusy = False
        self.answerQueue = []

    def SetSuperUser(self):
        self.logger.info('SetSuperUser')
        self.superuser = True

    def UnsetSuperUser(self):
        self.logger.info('UnsetSuperUser')
        self.superuser = False



