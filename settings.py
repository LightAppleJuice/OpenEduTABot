# coding=UTF-8
from ConfigParser import ConfigParser
from os import path


class settings():
    """
    Класс, в котором содержатся все настройки параметров бота, базы и т.д.
    """

    def __init__(self):
        _parser = ConfigParser()
        _parser.read(path.join(path.dirname(__file__), 'config.ini'))

        self.bot_token = _parser.get('COMMON', 'bot_token')

        self.database_name = _parser.get('DIRS', 'database_name')
        self.users_name = _parser.get('DIRS', 'users_name')
        self.log = _parser.get('DIRS', 'log')
        self.w2vec_model = _parser.get('DIRS', 'w2v_model')
        self.w2vec_dict = _parser.get('DIRS', 'w2v_dict')
        self.eng_rus_dict = _parser.get('DIRS', 'eng_rus_dict')
