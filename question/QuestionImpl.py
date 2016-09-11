from settings import settings
import logging
from MySQL_api.Commands import workWithData

__author__ = 'g.lavrentyeva'


class Question:
    def __init__(self, text, sender):
        self.config = settings()

        self.logger = logging.getLogger('BotLogger.Question')
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(self.config.log)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        self.sender = sender
        self.question = text
        self.answer = ''
        self.responder = ''
        self.responders = []
        self.stat_responder = 0

        self.logger.info('Init done')

    def SaveToDB(self):
        db = workWithData()
        if self.question and self.answer:
            db.addRow(self.question, self.answer)
        self.logger.info('Save question to DB: %s' % self.question)

    def DeleteFromDB(self):
        db = workWithData()
        if self.question:
            db.removeRow(self.question)
        self.logger.info('Remove question from DB: %s' % self.question)

