from settings import settings
import logging

__author__ = 'g.lavrentyeva'

class User:
    def __init__(self, id):
        self.config = settings()

        self.logger = logging.getLogger('BotLogger.User')
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(self.config.log)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        self.statistics = 0
        self.superuser = False
        self.id_token = id
        self.logger.info('Init done id: ', self.id_token)

    def SetSuperUser(self):
        self.logger.info('SetSuperUser id: ', self.id_token)
        self.superuser = True

    def UnsetSuperUser(self):
        self.logger.info('UnsetSuperUser id: ', self.id_token)
        self.superuser = False


