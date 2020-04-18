#!/usr/bin/python3

import os
import time
import json
import telebot
import requests
import datetime
from config import *
from telebot import apihelper
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


DEFAULT_CONFIG = './default_config'


apihelper.proxy = apihelper_proxy

def load_config(config_path):
    with open(config_path, 'rb') as conf:
        config = json.load(conf, encoding='utf8')
    return config


class Bot(telebot.TeleBot):
    def __init__(self, bot_token, user_list, command_list, admin_id):
        super().__init__(bot_token)
        bot = self
#        self.bot_token = bot_token
        self.user_list = user_list
        self.command_list = command_list
        self.admin_id = admin_id
#        self.bot = telebot.TeleBot(bot_token)


        def prepare_keyboard(self, *args):
            user_markup = telebot.types.ReplyKeyboardMarkup()
            user_markup.row(*args)
            return user_markup

        @bot.message_handler(commands=['start'])
        def handle_start(message):
            # if self.check_user(message.from_user.id) is True:
            #     bot.send_message(message.from_user.id, 'Starting', reply_markup=prepare_keyboard('/start'))
            # else:
            #     bot.send_message(message.from_user.id, 'What is your name?', reply_markup=prepare_keyboard('but1', 'but2'))
            bot.send_message(message.from_user.id, 'Starting', reply_markup=prepare_keyboard('/start'))

        @bot.message_handler(content_types=['text'])
        def handle_text(message):
            bot.send_message(admin_id, message.text)


# @bot.message_handler(content_types=['text'])
# def handle_text(message):
#
#     def send_photo(user_id):
#         directory = path + str(user_id) + "/"
#         files = os.listdir(directory)
#         for i in files:
#             now = datetime.datetime.now()
#             img = open(directory + i, 'rb')
#             arr = str(now) + ',' + str(message.from_user.id) + ',' + str(message.text) + ', ' +  str(img)
#             log = open(logfile, 'a')
#             log.write(arr + '\n')
#             log.close()
#             bot.send_photo(message.from_user.id, img)
#             img.close()
#
#     def logging():
#         now = datetime.datetime.now()
#         log = open(logfile, 'a')
#         arr = str(now) + ',' + str(message.from_user.id) + ',' +  u''.join((message.text)).encode('utf-8').strip()
#         log.write(arr + '\n')
#         log.close()
#
#     def handle_message(dashboard, lst):
#         for panelId in lst:
#             download_image(dashboard, panelId, user_id = message.from_user.id)
#         send_photo(message.from_user.id)
#         remove_img(message.from_user.id)
#
# #   Unauthorized users banner
#     if check_user(message.from_user.id) is False:
#         if message.text != 'Pwd12':
#             bot.send_message(message.from_user.id, 'You are not user of bot. Enter password or contact with administrators', reply_markup=user_markup0)
#             logging()
# #           who is try to use bot
#             bot.forward_message(admin_id, message.chat.id, message.message_id)
#             bot.send_message(admin_id, "User " + str(message.from_user.id) + " want to use this bot")
#         else:
# #       Adding user at white list by password
#             white_list.append(message.from_user.id)
#             bot.send_message(message.from_user.id, 'Password accepted. You are at user list now')
#
#
#     else:
# #   Adding user at white list by current user
#         if message.text.isdigit() is True and len(message.text)>=8:
#             try:
#                 bot.send_message(message.text, 'you are add at user list') # sayind new user about his adding in white list
#                 white_list.append(int(message.text))
#                 bot.send_message(message.from_user.id, str(white_list))
#             except:
#                 bot.send_message(message.from_user.id, 'Coudnt add user')
#
# #   Get list of all users
#         if message.text == 'List':
#             bot.send_message(message.from_user.id, str(white_list))
#
# #   Uncorrect command handling
#         if message.text not in commands:
#             bot.send_message(message.from_user.id, 'Please type start command', reply_markup=user_markup)
#
# #   Bot stop pooling
#         if message.text == 'Stop' and check_user(message.from_user.id) is True:
#             os.kill(os.getpid(), 9)
#
# #   Dashboar handling. Main functional
#         if message.text == 'bot-testing-dashboard':
#             user_markup2 = telebot.types.ReplyKeyboardMarkup()
#             user_markup2.row('Carbon agents localdomain', 'Metric recieved')
#             user_markup2.row('go back')
#             bot.send_message(message.from_user.id, 'going to Carbon agents localdomain dashboard', reply_markup=user_markup2)
#
#         if message.text in ['Metric recieved', 'Carbon agents localdomain'] and message.from_user.id in white_list:
#             dashboard = 'bot-testing-dashboard'
#             if message.text == 'Carbon agents localdomain':
#                 panelId = ('1')
#             if message.text == 'Metric recieved':
#                 panelId = ('2')
#             handle_message(dashboard, panelId)
#
#         if message.text == 'open-dashboard':
#             user_markup3 = telebot.types.ReplyKeyboardMarkup()
#             user_markup3.row('Commited points', 'Memussage')
#             user_markup3.row('go back')
#             bot.send_message(message.from_user.id, 'going to open-dashboard', reply_markup=user_markup3)
#
#         if message.text in ['Commited points', 'Memussage'] and message.from_user.id in white_list:
#             dashboard = 'open-dashboard'
#             if message.text == 'Commited points':
#                 panelId = ('1')
#             if message.text == 'Memussage':
#                 panelId = ('2')
#             handle_message(dashboard, panelId)
#
#         if message.text == 'go back':
#             bot.send_message(message.from_user.id, 'going back', reply_markup=user_markup)


# if __name__ == "__main__":
#     config = load_config(DEFAULT_CONFIG)
# #    print(config)
#     bot = Bot(config["bot_token"], config["user_list"], config["command_list"], config["admin_id"])
#        bot.polling(none_stop=True, timeout=30)
