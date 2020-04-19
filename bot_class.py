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

def get_grafana_dashboards(g_url, g_token):
    dashboards_array = []
    headers = {'Content-type': 'application/json'}
    headers.update(g_token)
    get_data_req = requests.get(g_url + '/api/search?query=&', headers=headers)
    pars_json = json.loads(get_data_req.text)
    for dash in pars_json:
        dashboards_array.append(dash['uri'][3::])
    return dashboards_array

def get_grafana_panels(g_token, g_url, e_dash):
    panels = []
    headers = {'Content-type': 'application/json'}
    headers.update(g_token)
#    dashboard_names = ['node-exporter-full', 'prometheus-2-0-stats', 'prometheus-stats']
    get_dashboard = requests.get(g_url + '/api/dashboards/db/' + e_dash, headers=headers)
    pars_json = json.loads(get_dashboard.text)
    for dashboard in pars_json['dashboard']['panels']:
#        print(dashboard['id'], dashboard['title'])
        panels.append({'id': dashboard['id'], 'title': dashboard['title']})
    return panels


class Bot(telebot.TeleBot):
    def __init__(self, bot_token, user_list, command_list, admin_id):
        super().__init__(bot_token)
        bot = self
        self.user_list = user_list
        self.command_list = command_list
        self.admin_id = admin_id
        self.dashboards = get_grafana_dashboards(grafana_url, grafana_token)

        def prepare_keyboard(lst, add_slash=False):
            user_markup = telebot.types.ReplyKeyboardMarkup()
            # if add_slash:
            #     for i in lst:
            #         user_markup.row('/' + i)
            #     return user_markup
            # for i in lst:
            #     user_markup.row(i)
            # return user_markup
            for i in lst:
                if add_slash:
                    user_markup.row('/' + i)
                else:
                    user_markup.row(i)
            return user_markup

        @bot.message_handler(commands=['start'])
        def handle_start(message):
            #     bot.send_message(message.from_user.id, 'What is your name?', reply_markup=prepare_keyboard('but1', 'but2'))
#            bot.send_message(message.from_user.id, 'Starting', reply_markup=prepare_keyboard('/start'))
            bot.send_message(message.from_user.id, 'Starting', reply_markup=prepare_keyboard(self.dashboards, add_slash=True))
#            bot.send_message(message.from_user.id, 'Starting', reply_markup=prepare_keyboard(get_grafana_dashboards(grafana_url, grafana_token)))

#        @bot.message_handler(commands=self.dashboards, content_types=['text'])
        @bot.message_handler(commands=self.dashboards)
        def handle_dashboards(message):
            panels = get_grafana_panels(grafana_token, grafana_url , message.text.replace('/',''))
            global panels_title
            panels_title = []
            for i in panels:
                panels_title.append(i['title'])
            bot.send_message(admin_id, 'valid dashboard', reply_markup=prepare_keyboard(panels_title))

        @bot.message_handler(content_types=['text'])
        def handle_text(message):
            print(panels_title)
            if message.text in panels_title:
                bot.send_message(admin_id, 'here prepare download image')
            else:
                bot.send_message(admin_id, 'coud not find dashboard: ' + message.text)



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
