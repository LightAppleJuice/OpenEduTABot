#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
from settings import settings
import logging


class workWithData:

    def __init__(self):
        self.config = settings()

        self.logger = logging.getLogger('BotLogger.workWithData')
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(self.config.log)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        self.connection = sqlite3.connect(self.config.database_name, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.cursor.execute('''CREATE TABLE if not exists questions (question Text(300) NOT NULL,
                                                                     answer Text(300),
                                                                     id_sender INTEGER  NOT NULL,
                                                                     id_responder INTEGER,
                                                                     wrongResponders Text(500),
                                                                     checked INTEGER,
                                                                     verify INTEGER)''')
        self.cursor.execute('''CREATE TABLE if not exists users (id_user COUNTER CONSTRAINT PrimaryKey PRIMARY KEY,
                                                                 status INTEGER)''')
        self.logger.info('Init done')

    def addQuestion(self, question, id_sender):
        """
        Добавление нового вопроса в таблицу
        :param question: string вопрос
        :param id_sender: integer id чата, задающего вопрос
        """
        sqlStr = "INSERT INTO questions VALUES ('{0}', '', {1}, 0, '', 0, 0)".format(question, id_sender)
        with self.connection:
            self.cursor.execute(sqlStr)
        self.logger.info('Added question: {0}'.format(question))

    def getQuestions(self, id_responder):
        """
        Получение всех неотвеченных вопросов из таблицы
        :param id_responder: integer id чата, отвечающего на вопрос
        :return: Список вопросов
        """
        sqlStr = "SELECT question, wrongResponders FROM questions WHERE id_sender <> {0} AND answer = ''"\
                 .format(id_responder)
        base = []
        with self.connection:
            temp = self.cursor.execute(sqlStr).fetchall()
        for elem in temp:
            if str(id_responder) not in elem[1]:
                base.append(elem[0])
        return base

    def deleteQuestion(self, question):
        """
        Удаление вопроса из таблицы
        :param question: string вопрос
        """
        sqlStr = "DELETE FROM questions WHERE question='{0}'".format(question)
        with self.connection:
            self.cursor.execute(sqlStr)
        self.logger.info('Deleted question: {0}'.format(question))

    def addAnswer(self, question, answer, id_responder):    #TODO защита от множественного редактирования
        """
        Добавление нового ответа в таблицу
        :param question: string вопрос
        :param answer: string ответ
        :param id_responder: integer id чата, ответившего на вопрос
        """
        sqlStr = "UPDATE questions SET answer='{1}', id_responder={2} WHERE question='{0}'"\
                 .format(question, answer, id_responder)
        with self.connection:
            self.cursor.execute(sqlStr)
        self.logger.info('Added answer: {0}'.format(answer))

    def getAnswers(self, id_sender=0, teacher=False):
        """
        Получение всех ответов из таблицы
        :param id_sender: integer id чата, задающего вопрос
        :param teacher: boolean является ли пользователь преподавателем
        :return: Словарь ответов на вопросы конкретного пользователя
        """
        if teacher:
            sqlStr = "SELECT question, answer FROM questions WHERE checked=1 AND verify=0".format(id_sender)
        else:
            sqlStr = "SELECT question, answer FROM questions WHERE id_sender = {0} AND answer <> '' AND checked=0"\
                     .format(id_sender)
        base = {}
        with self.connection:
            temp = self.cursor.execute(sqlStr).fetchall()
        for elem in temp:
            base[elem[0]] = elem[1]
        return base

    def checkAnswer(self, question):
        """
        Подтверждение корректности ответа, пользователем, задавшим вопрос
        :param question: string вопрос
        """
        sqlStr = "UPDATE questions SET checked=1 WHERE question='{0}'"\
                 .format(question)
        with self.connection:
            self.cursor.execute(sqlStr)
        self.logger.info('Checked answer from question: {0}'.format(question))

    def verifyAnswer(self, question):
        """
        Подтверждение корректности ответа, экспертом
        :param question: string вопрос
        """
        sqlStr = "UPDATE questions SET checked=1, verify=1 WHERE question='{0}'"\
                 .format(question)
        with self.connection:
            self.cursor.execute(sqlStr)
        self.logger.info('Verify answer from question: {0}'.format(question))

    def deleteAnswer(self, question):
        """
        Удаление неверного ответа
        :param question: string вопрос
        """
        sqlStr = "SELECT wrongResponders, id_responder FROM questions WHERE question = '{0}'".format(question)
        with self.connection:
            elem = self.cursor.execute(sqlStr).fetchall()
        if not elem[0][0]:
            wrongResponders = str(elem[0][1])
        else:
            wrongResponders = "{0}, {1}".format(elem[0][0], elem[0][1])
        sqlStr = "UPDATE questions SET answer='', id_responder=0, checked=0, verify=0, wrongResponders='{1}' WHERE " \
                 "question='{0}'".format(question, wrongResponders)
        with self.connection:
            self.cursor.execute(sqlStr)
        self.logger.info('Delete answer from question: {0}'.format(question))

    def getStat(self, id_responder):
        """
        Статистика количества ответов пользователя
        :param id_responder: integer id чата, ответившего на вопрос
        """
        answered = 0
        checked = 0
        verified = 0
        sqlStr = "SELECT COUNT(*) FROM questions WHERE id_responder = {0} AND answer <> '' AND checked=0"\
                 .format(id_responder)
        with self.connection:
            answered = self.cursor.execute(sqlStr).fetchall()
            if len(answered) > 1:
                raise Exception('Commands: Incorrect SQL response - too long answered count')
            answered = answered[0][0]

        sqlStr = "SELECT COUNT(*) FROM questions WHERE id_responder = {0} AND checked=1".format(id_responder)
        with self.connection:
            checked = self.cursor.execute(sqlStr).fetchall()
            if len(checked) > 1:
                raise Exception('Commands: Incorrect SQL response - too long checked count')
            checked = checked[0][0]

        sqlStr = "SELECT COUNT(*) FROM questions WHERE id_responder = {0} AND verify=1".format(id_responder)
        with self.connection:
            verified = self.cursor.execute(sqlStr).fetchall()
            if len(verified) > 1:
                raise Exception('Commands: Incorrect SQL response - too long verified count')
            verified = verified[0][0]
        return {'answered': answered, 'checked': checked, 'verified': verified}

    def addUser(self, id_user):

        sqlStr = "INSERT INTO users VALUES ({0}, 0)".format(id_user)
        with self.connection:
            try:
                self.cursor.execute(sqlStr)
            except sqlite3.IntegrityError:
                pass  # попытка повторной запист
        self.logger.info('Added user: {0}'.format(id_user))

    def getUsers(self):

        base = {}

        sqlStr = "SELECT * FROM users"
        with self.connection:
            temp = self.cursor.execute(sqlStr).fetchall()
        for elem in temp:
            cur_id = elem[0]
            if cur_id:
                base[cur_id] = self.getStat(cur_id)
            else:
                raise Exception('Commands: no user id in the table')
        return base

    def getUsersOld(self):
        """
        Получение всех пользователей из таблицы
        :return: Список id всех пользователей
        """

        base = {}

        sqlStr = "SELECT id_sender FROM questions"
        with self.connection:
            temp = self.cursor.execute(sqlStr).fetchall()
        for elem in temp:
            cur_id = elem[0]
            if cur_id:
                base[cur_id] = self.getStat(cur_id)
            else:
                raise Exception('Commands: no sender id in the table')

        sqlStr = "SELECT id_responder FROM questions"
        with self.connection:
            temp = self.cursor.execute(sqlStr).fetchall()
        for elem in temp:

            cur_id = elem[0]
            if cur_id:
                base[cur_id] = self.getStat(cur_id)

        sqlStr = "SELECT wrongResponders FROM questions"
        with self.connection:
            temp = self.cursor.execute(sqlStr).fetchall()
        for elem in temp:
            if elem[0]:
                users = elem[0].split(',')
                for cur_user in users:
                    cur_id = int(cur_user)
                    base[cur_id] = self.getStat(cur_id)

        return base

    def __del__(self):
        self.cursor.close()
        self.connection.close()
        self.logger.info('Closed')

class workWithUsersData:

    def __init__(self):
        self.config = settings()

        self.logger = logging.getLogger('BotLogger.workWithUsersData')
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(self.config.log)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        self.connection = sqlite3.connect(self.config.users_name, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.cursor.execute('''CREATE TABLE if not exists users (id_token COUNTER CONSTRAINT PrimaryKey PRIMARY KEY ,
                                                                     statistics INTEGER)''')

        self.logger.info('Init done')

    def addRow(self, id_token, statistics):
        """
        Добавление новой записи в таблицу
        :param question: string вопрос
        :param answer: string ответ
        """
        sqlStr = "INSERT INTO users VALUES ({0}, {1})".format(id_token, statistics)
        sqlStrDel = "DELETE FROM users WHERE id_token={0}".format(id_token)

        with self.connection:
            self.cursor.execute(sqlStrDel)
            self.cursor.execute(sqlStr)

        self.logger.info('Added user, id_token: %s' % id_token)

    def readRows(self):
        """
        Получаем все строки базы данных
        :return: список вопросов и ответов
        """
        base = {}
        with self.connection:
            temp = self.cursor.execute('SELECT * FROM users').fetchall()
        for elem in temp:
            base[elem[0]] = elem[1]
        self.logger.info('Read Rows')
        return base

    def removeRow(self, id_token):
        """
        Удаляем запись адреса
        :param question: string вопрос
        """
        sqlStrDel = "DELETE FROM users WHERE id_token={0}".format(id_token)
        with self.connection:
            self.cursor.execute(sqlStrDel)
        self.logger.info('Row removed id_token: %s' % id_token)

    def __del__(self):
        self.cursor.close()
        self.connection.close()
        self.logger.info('Closed')