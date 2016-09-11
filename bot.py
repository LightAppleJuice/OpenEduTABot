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
superhero_stickers = ['BQADBAAD0BQAArCKyAeOPZ8LYo3sYgI',
                      'BQADBAADyhQAArCKyAfyHUWLEWOT6wI',
                      'BQADBAADyBQAArCKyAfFQpfyRYjuWQI',
                      'BQADBAADxBQAArCKyAciOYhq7ejY7AI',
                      'BQADAgADQgAD7sShCsZ_Xcqe-dHLAg']


superhero_names = ['Зеленой стрелы',
                      'Капитана Америка',
                      'Халка',
                      'Железного Человека',
                      'Счастливого Единорога']

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

        self.waitingResponse = False

        @self.bot.message_handler(commands=['start'])
        def start(message):
            markup = telebot.types.ReplyKeyboardHide()
            self.bot.send_message(chat_id=message.chat.id, text='Здравствуй, {0}!\n'
                                                                'Я помогу тебе пройти курс Теория Игр. \n'
                                                                'Если у тебя возникнет вопрос, просто отправь его мне.\n'
                                                                'Я отвечу сам или перешлю его тому, кто сможет помочь.\n'
                                                                'Введи команду /superhero и ты можешь отвечать на вопросы других.'
                                  .format(message.from_user.first_name.encode('utf-8')), reply_markup=markup)
            if message.chat.id not in self.users.keys():
                self.users[message.chat.id] = User()
            self.logger.info('Added new user')
            self.bot.send_message(chat_id=message.chat.id, text='Что тебя интересует?')

        @self.bot.message_handler(commands=['help'])
        def help(message):
            self.bot.send_message(chat_id=message.chat.id, text='Я помогу тебе пройти курс Теория Игр. \n'
                                                                'Если у тебя возникнет вопрос, просто отправь его мне.\n'
                                                                'Я отвечу сам или перешлю его тому, кто сможет помочь.\n'
                                                                'Введи команду /superhero и ты можешь отвечать на вопросы других.'


        @self.bot.message_handler(commands=['superhero'])
        def superhero(message):
            if message.chat.id not in self.users.keys():
                self.users[message.chat.id] = User()
            markup = telebot.types.ReplyKeyboardHide()
            self.bot.send_message(chat_id=message.chat.id, text='Ты перешел в режим ответа на вопросы.',
                                  reply_markup=markup)
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
        def teacher(message):
            if message.chat.id not in self.users.keys():
                self.users[message.chat.id] = User()
            self.bot.send_message(chat_id=message.chat.id, text='Теперь вам будут приходить все отвеченные вопросы')
            markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add('Следующий вопрос', 'Прекратить')
            self.bot.send_message(chat_id=message.chat.id, text="Вопрос", reply_markup=markup)

        @self.bot.message_handler(regexp=u'✅')
        def apply_message(message):
            self.waitingResponse = False
            if message.chat.id not in self.users.keys():
                self.users[message.chat.id] = User()
            markup = telebot.types.ReplyKeyboardHide()
            for elem in self.questionsQueue:
                self.logger.info('Add answer to DB')
                if elem.sender == message.chat.id and elem in self.users[message.chat.id].answerQueue and elem.responder == ChatBotID:
                    db = workWithData()
                    db.addRow(elem.question, elem.answer)
                    if elem.stat_responder:
                        stat = self.users[elem.stat_responder].PlusStatistics()
                        if stat:
                            self.bot.send_sticker(chat_id=message.chat.id, data=superhero_stickers[stat - 1])
                            self.bot.send_message(chat_id=message.chat.id, text="Поздравляю! Ты достиг уровня " + superhero_names[stat-1] + "!", reply_markup=markup)
                    self.questionsQueue.remove(elem)
                    self.users[message.chat.id].answerQueue.remove(elem)
            self.bot.send_message(chat_id=message.chat.id, text="Вопрос добавлен. Cпасибо!\n Введи другой вопрос или перейди в режим ответа на вопросы.", reply_markup=markup)
            self.logger.info('Question added')
            if self.users[message.chat.id].answerQueue:
                self.logger.info('Sending answer from queue')
                markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                markup.add('\xE2\x9C\x85', '\xE2\x9D\x8C')
                self.bot.send_message(chat_id=message.chat.id,
                                      text="Кстати, я нашел ответ на вопрос, который ты мне задавал\n *Вопрос*: {0}\n *Ответ*: {1}".format(
                                                                    self.users[message.chat.id].answerQueue[0].question,
                                                                    self.users[message.chat.id].answerQueue[0].answer),
                                                                    reply_markup=markup, parse_mode='Markdown')
                self.bot.send_message(chat_id=message.chat.id,
                                      text="Оцени полученный ответ и мы сможем продолжить.",
                                      reply_markup=markup)
                self.waitingResponse = True
                self.users[message.chat.id].answerQueue[0].stat_responder = self.users[message.chat.id].answerQueue[
                    0].responder
                self.users[message.chat.id].answerQueue[0].responder = ChatBotID

        @self.bot.message_handler(regexp=u'❌')
        def cancel_message(message):
            self.waitingResponse = False
            if message.chat.id not in self.users.keys():
                self.users[message.chat.id] = User()
            markup = telebot.types.ReplyKeyboardHide()
            for elem in self.questionsQueue:
                self.logger.info('Clear responder and answer')
                if elem.sender == message.chat.id and elem in self.users[message.chat.id].answerQueue:
                    elem.responder = ''
                    elem.answer = ''
                    self.users[message.chat.id].answerQueue.remove(elem)
            self.bot.send_message(chat_id=message.chat.id, text="Вопрос направлен пользователю", reply_markup=markup)
            self.bot.send_message(chat_id=message.chat.id, text="Как только получу ответ - сразу же сообщу\n"
                                                                "А пока задай мне другой вопрос или перейди в режим ответа на вопросы.")

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
        def next_message(message):
            if message.chat.id not in self.users.keys():
                self.users[message.chat.id] = User()
            markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add('Следующий вопрос', 'Прекратить')
            for elem in self.questionsQueue:
                # a = elem.responder
                # b=elem.responders
                if (not elem.responder) and (message.chat.id not in elem.responders):
                    elem.responder = message.chat.id
                    elem.responders.append(message.chat.id)
                    self.bot.send_message(chat_id=message.chat.id, text="Помоги мне, пожалуйста.")
                    self.bot.send_message(chat_id=message.chat.id, text=elem.question, reply_markup=markup)
                    break
            else:
                markup = telebot.types.ReplyKeyboardHide()
                self.users[message.chat.id].UnsetSuperUser()
                self.bot.send_message(chat_id=message.chat.id, text="Больше вопросов не будет. Выхожу из режима "
                                                                    "SuperUser.", reply_markup = markup)

        @self.bot.message_handler(regexp=ur'Прекратить')
        def stop_message(message):
            if message.chat.id not in self.users.keys():
                self.users[message.chat.id] = User()
            self.users[message.chat.id].UnsetSuperUser()
            self.bot.send_message(chat_id=message.chat.id, text="Больше вопросов не будет")

        @self.bot.message_handler(func=lambda message: True, content_types=['text'])
        def parse_message(message):
            markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            text = message.text.encode('utf-8')
            if message.chat.id not in self.users.keys():
                self.users[message.chat.id] = User()
            if self.users[message.chat.id].superuser:
                for elem in self.questionsQueue:
                    if elem.responder == message.chat.id:
                        elem.answer = text
                        self.users[elem.sender].answerQueue.append(elem)
                        break
                markup.add('Следующий вопрос', 'Прекратить')
                self.bot.send_message(chat_id=message.chat.id, text='Спасибо!',
                                      reply_markup=markup)
                for elem in self.questionsQueue:
                    # a = elem.responder
                    # b=elem.responders
                    if (not elem.responder) and (message.chat.id not in elem.responders):
                        elem.responder = message.chat.id
                        elem.responders.append(message.chat.id)
                        self.bot.send_message(chat_id=message.chat.id, text="Помоги мне, пожалуйста.")
                        self.bot.send_message(chat_id=message.chat.id, text=elem.question, reply_markup=markup)
                        break
                else:
                    markup = telebot.types.ReplyKeyboardHide()
                    self.users[message.chat.id].UnsetSuperUser()
                    self.bot.send_message(chat_id=message.chat.id,
                                          text="Больше вопросов не будет. Выхожу из режима SuperUser.", reply_markup=markup)

            else:
                if self.waitingResponse:
                    self.bot.send_message(chat_id=message.chat.id,
                                          text="Пожалуйста, оцени предыдущий ответ.")
                    return
                question = Question(text, message.chat.id)
                self.questionsQueue.append(question)
                self.logger.info('Question added: %s' % text)
                answer, confidence = self.text_classifier.give_answer(text)
                answer = answer.encode('utf-8')
                if confidence > 0.7:
                    question.answer = answer
                    question.responder = ChatBotID
                    self.users[message.chat.id].answerQueue.append(question)
                    self.logger.info('Answer and responder added: %s' % answer)
                    markup.add('\xE2\x9C\x85', '\xE2\x9D\x8C')
                    self.bot.send_message(chat_id=message.chat.id, text=answer+" "+str(confidence), reply_markup=markup)
                    self.waitingResponse = True
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
