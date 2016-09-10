#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Main Bot Class

from settings import settings
from nlp_part.TextMatcher import TextClassifier
import telebot
import logging
from MySQL_api.Commands import workWithUsersData
from user.UserImpl import User


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

            self.bot.send_message(chat_id=message.chat.id, text='Что тебя интересует?')

        @self.bot.message_handler(commands=['help'])
        def help(message):
            self.bot.send_message(chat_id=message.chat.id, text='Я помогу тебе пройти курс Теория Игр. \n'
                                                                'Если у тебя возникнет вопрос, просто отправь его мне.\n'
                                                                'Я отвечу сам или перешлю его тому, кто сможет помочь.')


        @self.bot.message_handler(commands=['superuser'])
        def help(message):
            self.bot.send_message(chat_id=message.chat.id, text='Теперь вам будут приходить запросы')
            markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add('Следующий вопрос', 'Прекратить')
            self.bot.send_message(chat_id=message.chat.id, text="Вопрос", reply_markup=markup)

        @self.bot.message_handler(commands=['teacher'])
        def help(message):
            self.bot.send_message(chat_id=message.chat.id, text='Теперь вам будут приходить все отвеченные вопросы')
            markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add('Следующий вопрос', 'Прекратить')
            self.bot.send_message(chat_id=message.chat.id, text="Вопрос", reply_markup=markup)

        @self.bot.message_handler(regexp=u'✅')
        def about_message(message):
            markup = telebot.types.ReplyKeyboardHide()
            self.bot.send_message(chat_id=message.chat.id, text="Вопрос добавлен", reply_markup=markup)

        @self.bot.message_handler(regexp=u'❌')
        def about_message(message):
            markup = telebot.types.ReplyKeyboardHide()
            self.bot.send_message(chat_id=message.chat.id, text="Вопрос направлен пользователю", reply_markup=markup)
            self.bot.send_message(chat_id=message.chat.id, text="Как только получу ответ - сразу же сообщу")
            self.bot.send_message(chat_id=message.chat.id, text="А пока задай другой вопрос")

        @self.bot.message_handler(regexp=ur'Следующий вопрос')
        def about_message(message):
            markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add('Следующий вопрос', 'Прекратить')
            self.bot.send_message(chat_id=message.chat.id, text="Вопрос", reply_markup=markup)

        @self.bot.message_handler(regexp=ur'Прекратить')
        def about_message(message):
            self.bot.send_message(chat_id=message.chat.id, text="Больше вопросов не будет")

        @self.bot.message_handler(func=lambda message: True, content_types=['text'])
        def parse_message(message):
            markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add('\xE2\x9C\x85', '\xE2\x9D\x8C')
            question = message.text.encode('utf-8')
            answer, confidence = self.text_classifier.give_answer(question)
            if confidence > 0.7:
                self.bot.send_message(chat_id=message.chat.id, text='Для пользователя - Ответ', reply_markup=markup)
                self.bot.send_message(chat_id=message.chat.id, text=answer+" "+str(confidence), reply_markup=markup)
            else:
                self.bot.send_message(chat_id=message.chat.id, text='Перенаправляю вопрос', reply_markup=markup)
                self.bot.send_message(chat_id=message.chat.id, text=answer+" "+str(confidence), reply_markup=markup)
            self.bot.send_message(chat_id=message.chat.id, text='Для суперпользователя - Благодарность за ответ', reply_markup=markup)

    def __del__(self):
        self.bot.stop_polling()
        self.logger.info('Bot deinit done')

    def start(self):
        self.bot.polling(none_stop=True)

    def LoadUsersFromDB(self):
        loader = workWithUsersData()
        loadedUsers = loader.readRows()
        users = []
        for i in loadedUsers.keys():
            user = User(loadedUsers)
            user.statistics = loadedUsers[i]
            users.append(user)
        self.logger.info('Users loaded from DB')
        return users


if __name__ == '__main__':
    Bot = TeacherAssistantBot()
    Bot.start()
