#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Main Bot Class

from settings import settings
from nlp_part.TextMatcher import TextClassifier
from question.QuestionImpl import Question
import telebot
import logging
from MySQL_api.Commands import workWithUsersData
from MySQL_api.Commands import workWithData
from user.UserImpl import User

ChatBotID = 1

class TeacherAssistantBot:

    def __init__(self):
        # Bot initialization
        self.config = settings()
        self.bot = telebot.TeleBot(self.config.bot_token)

        # Logger initialization
        self.logger = logging.getLogger('BotLogger')
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(self.config.log)

        # Users db
        self.users = self.LoadUsersFromDB()
        self.users[ChatBotID] = User()
        # Questions db
        self.questionsQueue = []

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        self.logger.info('NLP init')
        self.text_classifier = TextClassifier()

        self.logger.info('Bot init done')

        @self.bot.message_handler(commands=['start'])
        def start(message):
            self.bot.send_message(chat_id=message.chat.id, text='Здравствуй, {0}!\n'
                                                                'Я помогу тебе пройти курс Теория Игр. \n'
                                                                'Если у тебя возникнет вопрос, просто отправь его мне.\n'
                                                                'Я отвечу сам или перешлю его тому, кто сможет помочь.'
                                  .format(message.from_user.first_name.encode('utf-8')))
            self.users[message.chat.id] = User()
            self.logger.info('Added new user')
            self.bot.send_message(chat_id=message.chat.id, text='Что тебя интересует?')

        @self.bot.message_handler(commands=['help'])
        def help(message):
            self.bot.send_message(chat_id=message.chat.id, text='Я помогу тебе пройти курс Теория Игр. \n'
                                                                'Если у тебя возникнет вопрос, просто отправь его мне.\n'
                                                                'Я отвечу сам или перешлю его тому, кто сможет помочь.')


        @self.bot.message_handler(commands=['superuser'])
        def help(message):
            self.bot.send_message(chat_id=message.chat.id, text='Ты перешел в режим ответа на вопросы.')
            self.users[message.chat.id].SetSuperUser()

            for elem in self.questionsQueue:
                if (not elem.responder) and (message.chat.id not in elem.responders):
                    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                    markup.add('Следующий вопрос', 'Прекратить')
                    elem.responder = message.chat.id
                    elem.responders.append(message.chat.id)
                    self.bot.send_message(chat_id=message.chat.id, text="Помоги мне, пожалуйста.")
                    self.bot.send_message(chat_id=message.chat.id, text=elem.question, reply_markup=markup)
                    break

        @self.bot.message_handler(commands=['teacher'])
        def help(message):
            self.bot.send_message(chat_id=message.chat.id, text='Теперь вам будут приходить все отвеченные вопросы')
            markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add('Следующий вопрос', 'Прекратить')
            self.bot.send_message(chat_id=message.chat.id, text="Вопрос", reply_markup=markup)

        @self.bot.message_handler(regexp=u'✅')
        def about_message(message):
            self.users[message.chat.id].isBusy = False
            markup = telebot.types.ReplyKeyboardHide()
            for elem in self.questionsQueue:
                self.logger.info('Add answer to DB')
                if elem.sender == message.chat.id and elem not in self.users[message.chat.id].answerQueue:
                    db = workWithData()
                    db.addRow(elem.question, elem.answer)
                    self.users[elem.responder].PlusStatistics()
            self.bot.send_message(chat_id=message.chat.id, text="Вопрос добавлен", reply_markup=markup)
            self.logger.info('Question added')
            if self.users[message.chat.id].answerQueue:
                self.logger.info('Sending answer from queue')
                markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                markup.add('\xE2\x9C\x85', '\xE2\x9D\x8C')
                self.bot.send_message(chat_id=message.chat.id, text="Ответ на твой вопрос: {0}\n\n{1}".format(
                                                                    self.users[message.chat.id].answerQueue[0].question,
                                                                    self.users[message.chat.id].answerQueue[0].answer),
                                                                    reply_markup=markup)
                self.users[message.chat.id].answerQueue.pop(0)

        @self.bot.message_handler(regexp=u'❌')
        def about_message(message):
            markup = telebot.types.ReplyKeyboardHide()
            for elem in self.questionsQueue:
                self.logger.info('Clear responder and answer')
                if elem.sender == message.chat.id and elem not in self.users[message.chat.id].answerQueue:
                    elem.responser = ''
                    elem.answer = ''
            self.bot.send_message(chat_id=message.chat.id, text="Вопрос направлен пользователю", reply_markup=markup)
            self.bot.send_message(chat_id=message.chat.id, text="Как только получу ответ - сразу же сообщу")

            if self.users[message.chat.id].answerQueue:
                self.logger.info('Sending answer from queue')
                markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                markup.add('\xE2\x9C\x85', '\xE2\x9D\x8C')
                self.bot.send_message(chat_id=message.chat.id, text="Ответ на твой вопрос: {0}\n\n{1}".format(
                                                                    self.users[message.chat.id].answerQueue[0].question,
                                                                    self.users[message.chat.id].answerQueue[0].answer),
                                                                    reply_markup=markup)
                self.users[message.chat.id].answerQueue.pop(0)

        @self.bot.message_handler(regexp=ur'Следующий вопрос')
        def about_message(message):
            markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add('Следующий вопрос', 'Прекратить')
            self.bot.send_message(chat_id=message.chat.id, text="Вопрос", reply_markup=markup)

        @self.bot.message_handler(regexp=ur'Прекратить')
        def about_message(message):
            self.users[message.chat.id].UnsetSuperUser()
            self.bot.send_message(chat_id=message.chat.id, text="Больше вопросов не будет")

        @self.bot.message_handler(func=lambda message: True, content_types=['text'])
        def parse_message(message):
            markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add('\xE2\x9C\x85', '\xE2\x9D\x8C')
            text = message.text.encode('utf-8')
            if message.chat.id not in self.users.keys():
                self.users[message.chat.id] = User()
            if self.users[message.chat.id].superuser:
                for elem in self.questionsQueue:
                    if elem.responder == message.chat.id:
                        elem.answer = text
                        self.users[elem.sender].answerQueue.append(elem)
                        break
                self.bot.send_message(chat_id=message.chat.id, text='Спасибо!',
                                      reply_markup=markup)
            else:
                question = Question(text, message.chat.id)
                self.questionsQueue.append(question)
                self.logger.info('Question added: ', text)
                answer, confidence = self.text_classifier.give_answer(text)
                if confidence > 0.7:
                    question.answer = answer
                    question.responder = ChatBotID
                    self.logger.info('Answer and responder added: ', answer)
                    self.bot.send_message(chat_id=message.chat.id, text=answer+" "+str(confidence), reply_markup=markup)
                else:
                    self.bot.send_message(chat_id=message.chat.id, text='Я не уверен в ответе\n'
                                                                        'Я перенаправлю твой вопрос и напишу тебе, как только получу ответ.')
                    #self.bot.send_message(chat_id=message.chat.id, text=answer+" "+str(confidence), reply_markup=markup)


    def __del__(self):
        self.bot.stop_polling()
        self.logger.info('Bot deinit done')

    def start(self):
        self.bot.polling(none_stop=True)

    def LoadUsersFromDB(self):
        loader = workWithUsersData()
        loadedUsers = loader.readRows()
        users = {}
        for i in loadedUsers.keys():
            user = User()
            user.statistics = loadedUsers[i]
            users[i] = user
        self.logger.info('Users loaded from DB')
        return users


if __name__ == '__main__':
    Bot = TeacherAssistantBot()
    Bot.start()
