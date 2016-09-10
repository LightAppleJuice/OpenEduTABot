import requests
from settings import settings
import os
import logging
import io
import numpy as np
import sys
import urllib2

__author__ = 'g.lavrentyeva'

class Question:
    def __init__(self):
        self.config = settings()

        self.logger = logging.getLogger('BotLogger.Question')
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(self.config.log)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        self.sender = ''
        self.question = ''
        self.answer = ''
        self.responder = ''
