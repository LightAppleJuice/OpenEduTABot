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
                                                                     answer Text(300) NOT NULL)''')

        self.logger.info('Init done')

    def addRow(self, question, answer):
        """
        Добавление новой записи в таблицу
        :param question: string вопрос
        :param answer: string ответ
        """
        sqlStr = "INSERT INTO questions VALUES ('{0}', '{1}')".format(question, answer)
        sqlStrDel = "DELETE FROM questions WHERE question='{0}'".format(question)

        with self.connection:
            self.cursor.execute(sqlStrDel)
            self.cursor.execute(sqlStr)

    def readRows(self):
        """
        Получаем все строки базы данных
        :return: список вопросов и ответов
        """
        base = {}
        with self.connection:
            temp = self.cursor.execute('SELECT * FROM questions').fetchall()
        for elem in temp:
            base[elem[0]] = elem[1]
        return base

    def removeRow(self, question):
        """
        Удаляем запись адреса
        :param question: string вопрос
        """
        sqlStrDel = "DELETE FROM questions WHERE question='{0}'".format(question)
        with self.connection:
            self.cursor.execute(sqlStrDel)

        self.logger.info('Added question: %s' % question)

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
