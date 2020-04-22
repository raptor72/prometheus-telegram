#!/usr/bin/python3

import os
import re
import ast
import sys
import json
import socket
import logging
import datetime
import subprocess
from bot import Bot
from optparse import OptionParser
from collections import namedtuple
from datetime import datetime as dt

Alarm = namedtuple('Alarm', 'alertname startsAt node')

DEFAULT_CONFIG = './default_config'

REQUEST_PARAMS = {
    'Host': 'Host',
    'User-Agent': 'User-Agent',
    'Content-Length': 'Content-Length',
    'Content-Type': 'Content-Type'
}


def load_config(config_path):
    with open(config_path, 'rb') as conf:
        config = json.load(conf, encoding='utf8')
    return config

def read_all(sock, maxbuff, TIMEOUT=5):
    data = b''
    sock.settimeout(TIMEOUT)
    while True:
        buf = sock.recv(maxbuff)
        data += buf
        if not buf or b'\r\n\r\n' in data:
            break
    return data


def parse_request(request):
    headers = {}
    parsed = request.split('\r\n\r\n')[0].split(' ')
    method = parsed[0]
    for i in request.split('\r\n'):
        try:
            headers.update({REQUEST_PARAMS[i.split(':')[0]]: i.split(':')[1].strip()})
        except:
            continue
    return method, headers



def generate_response(request):
    method, headers = parse_request(request)
    if method not in ['POST']:
        return ('HTTP/1.1 405 Method not allowed\r\n', 405, None)
    if headers == {}:
        return ('HTTP/1.1 422 Can not parse headers format\r\n', 422, None)
    if not 'Alertmanager' in headers['User-Agent']:
        return ('HTTP/1.1 400 Unsupported sender\r\n', 400, None)
    if not 'json' in headers['Content-Type']:
        return ('HTTP/1.1 400 Unsupported Content-Type\r\n', 400, None)
    alarm_description = request.split('\r\n\r\n')[1]
    return ('HTTP/1.1 200 OK\r\n', 200, alarm_description)


def make_current_alarm(alarm_description):
    d = {}
    try:
        d = ast.literal_eval(alarm_description)
    except SyntaxError:
        logging.error('Uncorrect json syntax in received alarm_description')
    try:
        alertname = d['alerts'][0]['labels']['alertname']
    except:
        logging.error('Could not parse alertname')
    startsAt = datetime.datetime.strptime(d['alerts'][0]['startsAt'][:26], '%Y-%m-%dT%H:%M:%S.%f').strftime('%Y-%m-%dT%H:%M:%S.%f')
    node = d['externalURL']
    current_alarm = Alarm(alertname, startsAt, node)
    return current_alarm

def check_config(config_path):
    try:
        with open(config_path, 'rb') as conf:
            data = json.load(conf, encoding='utf8')
        if len(data) != 5:
            logging.error(f'Wrong count of config params. Should be 8 but exists is {len(data)}')
            return False
        for key in data.keys():
            if key in ['apihelper_proxy', 'grafana_token', 'grafana_url', 'bot_token', 'users_file']:
                continue
            else:
                logging.error(f'Wrong config walue for {key}')
                return False
    except json.decoder.JSONDecodeError:
         logging.error('Syntax error in config file')
         return False
    return True

def run(host, port, conf):
    all_alarms = []
    config = load_config(conf)
    bot = Bot(config)
    with open(config['users_file'], 'rb') as users:
        users = json.load(users, encoding='utf8')
    logging.debug(f'Firs load users is: {users}')
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
#    server_socket.bind(('172.17.0.2', port))
    server_socket.listen()

    pid = os.fork()
    if pid != 0:
        bot.polling(none_stop=True, timeout=30)
    else:
        while True:
            client_socket, addr = server_socket.accept()
            request = read_all(client_socket, maxbuff=2048)
            logging.info(f'request is: {request}')
            logging.info(f'address is: {addr}')
            if len(request.strip()) == 0:
                client_socket.close()
                continue
            if request:
                response_prase, code, alarm_description = generate_response(request.decode('utf-8'))
                client_socket.sendall((response_prase + str(code)).encode())
                current_alarm = make_current_alarm(alarm_description)
                if not current_alarm in all_alarms:
                    all_alarms.append(current_alarm)
                    if os.path.getmtime(config['users_file']) > dt.today().timestamp():
                        with open(config['users_file'], 'rb') as users:
                            users = json.load(users, encoding='utf8')
                    logging.info(f'Users is {users}')
                    if len(users) > 0:
                        for user in users:
                            if users[user] in ['*', 'all', '\w', 'All', 'ALL']:
                                res = re.findall('\w', current_alarm.alertname.lower())
                            else:
                                res = re.findall(r'%s' % re.escape(users[user].lower()), current_alarm.alertname.lower())
                            if res:
                                bot.send_message(user, alarm_description)
            client_socket.close()
    server_socket.close()

if __name__ == '__main__':
    op = OptionParser()
    op.add_option('-p', '--port', action='store', type=int, default=8080)
    op.add_option('-H', '--host', action='store', type=str, default='127.0.0.1')
    op.add_option('-c', '--config', action='store', type=str, default=DEFAULT_CONFIG)
    op.add_option('-l', '--log', action='store', default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    logging.info(f'Bind address is {opts.host}')
    logging.info(f'Starting listen at {opts.port}')
    if check_config(opts.config):
        logging.info(f'Use correct configuration file {opts.config}')
        try:
            run(opts.host, opts.port, opts.config)
        except:
            logging.exception('Fatal unexpected error')
    else:
        logging.error(f'Used wrong configuration file')
