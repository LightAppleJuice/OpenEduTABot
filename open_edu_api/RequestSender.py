import requests
from settings import settings
import os
import logging
import io
import numpy as np
import sys
import urllib2

__author__ = 'g.lavrentyeva'


class RequestSender:
    def __init__(self):
        self.config = settings()

        self.logger = logging.getLogger('BotLogger.RequestSender')
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(self.config.log)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def getCourseList(self):
        self.logger.info('Sending Request getCourseList')
        #params = {'token': 123, 'limit': 1}
        try:
            r = requests.get("https://openedu.ru/api/course_structure/v0/courses/?")
            parsed_string = r.json()
            if r.status_code != 200:
                raise Exception('OpenEdu exception: Bad response')

            if 'error' in parsed_string:
                if parsed_string['error'] == 403:
                    raise Exception('OpenEdu exception: Access denied')
                if parsed_string['error'] == 404:
                    raise Exception('OpenEdu exception: Object not found')
                if parsed_string['error'] == 402:
                    raise Exception('OpenEdu exception: Incorrect request')
                else:
                    raise Exception('Muzis exception: Unknown exception')
            else:
                print('Ok')
        except Exception as inst:
            self.logger.warning('getCourseList(): ' + str(inst.message))
        except:
            self.logger.warning('getCourseList(): ' + str(sys.exc_info()[0]))


# test
rs = RequestSender()
rs.getCourseList()