#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
from settings import settings


class workWithData:

    def __init__(self):
        config = settings()
        self.connection = sqlite3.connect(config.database_name, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.cursor.execute('''CREATE TABLE if not exists questions (question Text(300) NOT NULL,
                                                                     answer Text(300) NOT NULL)''')

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

    def __del__(self):
        self.cursor.close()
        self.connection.close()