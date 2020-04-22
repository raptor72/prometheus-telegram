#!/usr/bin/python3

import os
import re
import time
import json
import telebot
import logging
import requests
import datetime
from pathlib import Path
from telebot import apihelper
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



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
    get_dashboard = requests.get(g_url + '/api/dashboards/db/' + e_dash, headers=headers)
    pars_json = json.loads(get_dashboard.text)
    for dashboard in pars_json['dashboard']['panels']:
        panels.append({'id': dashboard['id'], 'title': dashboard['title']})
    return panels


def download_image(dasboard, panelId, g_url, g_token, delta=12):
    now = datetime.datetime.now()
    past = datetime.datetime.now() - datetime.timedelta(hours=delta)
    tsnow = str(time.mktime(now.timetuple())).split('.')[0] + str(float(now.microsecond) / 1000000).split('.')[1][0:3]
    tspast = str(time.mktime(past.timetuple())).split('.')[0] + str(float(now.microsecond) / 1000000).split('.')[1][0:3]
    url = ''.join([g_url, '/render/dashboard-solo/db/', dasboard, '?orgId=1&from=', tspast, '&to=', tsnow, '&panelId=', panelId, '&width=1000&height=500'])
    rec =  requests.get(url, verify = False, headers = g_token, timeout = 30)
    return rec.content


def update_users_regexp(config_path, frame):
    path = Path(config_path)
    data = json.loads(path.read_text(encoding='utf-8'))
    data.update(frame)
    path.write_text(json.dumps(data), encoding='utf-8')


class Bot(telebot.TeleBot):
    def __init__(self, config):
        super().__init__(config['bot_token'])
        bot = self
        self.dashboards = get_grafana_dashboards(config['grafana_url'], config['grafana_token'])
        apihelper.proxy = config['apihelper_proxy']

        def prepare_keyboard(lst, add_slash=False):
            user_markup = telebot.types.ReplyKeyboardMarkup()
            if add_slash:
                for i in lst:
                    user_markup.row('/' + i)
                return user_markup
            else:
                for i in lst:
                    user_markup.row(i)
                user_markup.row('go back')
            return user_markup


        @bot.message_handler(commands=['start'])
        def handle_start(message):
            bot.send_message(message.from_user.id, 'Bot starting. Add your alarm subscription by /regexp command. For more details use /help',
                             reply_markup=prepare_keyboard(self.dashboards, add_slash=True))

        @bot.message_handler(commands=['help'])
        def handle_help(message):
            bot.send_message(message.from_user.id, """
            Use /regexp to add your alarm subscription. Type the word after spase. For exhample '/regexp mem'. 
            Case is doesn't matter: 'mem' or 'Mem' will work the same.
            If you need more than one kind of alarm type many words split by '|'. For exhample 'mem|cpu|load'.
            If you wish recieve all alarms type * or all.
            If you want check your subscribe use commant /list
            """
                             )

        @bot.message_handler(commands=['regexp'])
        def handle_regexp(message):
            try:
                expression = message.text.split(" ")[1]
                try:
                    print(expression)
                    update_users_regexp('users', {str(message.from_user.id): str(expression)})
                    bot.send_message(message.from_user.id, 'expression update for {}'.format(expression))
                except:
                    logging.info('Could not update regexp')
            except IndexError:
                bot.send_message(message.from_user.id, 'Type correct regexp')

        @bot.message_handler(commands=['list'])
        def handle_regexp(message):
            path = Path('users')
            data = json.loads(path.read_text(encoding='utf-8'))
            try:
                expression = data[str(message.from_user.id)]
                bot.send_message(message.from_user.id, 'Your regexp is: {}'.format(expression))
            except KeyError:
                bot.send_message(message.from_user.id, 'You are not subscriber. Add your regexp. If You have any questions use /help')


        @bot.message_handler(commands=self.dashboards)
        def handle_dashboards(message):
            global dashboard, panels_title, panels
            dashboard = message.text
            panels = get_grafana_panels(config['grafana_token'], config['grafana_url'] , message.text.replace('/',''))
            panels_title = []
            for i in panels:
                panels_title.append(i['title'])
            bot.send_message(message.from_user.id, 'Valid dashboard', reply_markup=prepare_keyboard(panels_title))

        @bot.message_handler(content_types=['text'])
        def handle_text(message):

            def get_id_by_title(panels, title):
                for i in panels:
                    if i['title'] == title:
                        return i['id']

            try:
                # print(globals())
                if message.text == 'go back':
                    bot.send_message(message.from_user.id, 'going back', reply_markup=prepare_keyboard(self.dashboards, add_slash=True))
                if message.text in panels_title:
                    try:
                        id = get_id_by_title(panels, message.text)
                        bot.send_message(message.from_user.id, 'Prepare download image')
                        screenshot = download_image(dashboard.replace('/',''), str(id), config['grafana_url'], config['grafana_token'])
                        bot.send_photo(message.from_user.id, screenshot)
                    except:
                        print('Could not send image')
                else:
                    if message.text != 'go back':
                        bot.send_message(message.from_user.id, 'Could not find dashboard: ' + message.text)
            except NameError:
                 bot.send_message(message.from_user.id, 'You should choice correct dashboard or type right command',
                                  reply_markup=prepare_keyboard(self.dashboards, add_slash=True))


