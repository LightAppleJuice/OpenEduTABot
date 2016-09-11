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

    def PlusStatistics(self):
        self.logger.info('Plus statictics for user')
        self.statistics += 1
        if self.statistics == 1:
            return 1
        elif self.statistics == 10:
            return 2
        elif self.statistics == 100:
            return 3
        elif self.statistics == 200:
            return 4
        elif self.statistics == 300:
            return 5
        else:
            return 0





