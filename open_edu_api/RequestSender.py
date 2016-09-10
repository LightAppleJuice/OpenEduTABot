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
            if r.status_code == 200:
                print('Ok')
            else:
                if r.status_code == 401:
                    raise Exception('OpenEdu exception: Unauthorized user')
                else:
                    raise Exception('OpenEdu exception: Unknown exception')
        except Exception as inst:
            self.logger.warning('getCourseList(): ' + str(inst.message))
        except:
            self.logger.warning('getCourseList(): ' + str(sys.exc_info()[0]))

    def getLecturerList(self):
        self.logger.info('Sending Request getLecturerList')
        params = {'token': 123, 'limit': 1}
        try:
            r = requests.get("http://lectoriy.mipt.ru/api/v1/lecturer")
            parsed_string = r.json()
            if r.status_code == 200:
                print('Ok')
            else:
                if r.status_code == 401:
                    raise Exception('OpenEdu exception: Unauthorized user')
                else:
                    raise Exception('OpenEdu exception: Unknown exception')
        except Exception as inst:
            self.logger.warning('getCourseList(): ' + str(inst.message))
        except:
            self.logger.warning('getCourseList(): ' + str(sys.exc_info()[0]))

    def getToken(self):
        self.logger.info('Sending Request getLecturerList')
        params = {'token': 'hMtae8mrtwOoqDF3T0d2CnD5APJYBoMT', 'limit': 1}
        try:
            r = requests.get("http://lectoriy.mipt.ru/api/v1/main", data=params)
            parsed_string = r.json()
            if r.status_code == 200:
                print('Ok')
            else:
                if r.status_code == 401:
                    raise Exception('OpenEdu exception: Unauthorized user')
                else:
                    raise Exception('OpenEdu exception: Unknown exception')
        except Exception as inst:
            self.logger.warning('getCourseList(): ' + str(inst.message))
        except:
            self.logger.warning('getCourseList(): ' + str(sys.exc_info()[0]))


# test
rs = RequestSender()
rs.getToken()