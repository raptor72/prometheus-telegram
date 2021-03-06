#!/usr/bin/python3

import os
import re
import sys
import json
import socket
import logging
import datetime
from bot import Bot
from optparse import OptionParser
from collections import namedtuple
from datetime import datetime as dt

Alarm = namedtuple('Alarm', 'alertname status startsAt node')

DEFAULT_CONFIG = './default_config'

REQUEST_PARAMS = {
    'Host': 'Host',
    'User-Agent': 'User-Agent',
    'Content-Length': 'Content-Length',
    'Content-Type': 'Content-Type'
}


def load_users(users_file):
    with open(users_file, 'rb') as users:
        users = json.load(users, encoding='utf8')
    return users


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


def make_current_alarm(response_prase, code, alarm_description):
    current_alarm = None
    if code != 200:
        logging.error(f'{response_prase}')
        return current_alarm
    try:
        d = json.loads(alarm_description)
        try:
            alertname = d['alerts'][0]['labels']['alertname']
            status = d['status']
            startsAt = datetime.datetime.strptime(d['alerts'][0]['startsAt'][:26], '%Y-%m-%dT%H:%M:%S.%f').strftime(
                '%Y-%m-%dT%H:%M:%S.%f')
            node = d['externalURL']
            current_alarm = Alarm(alertname, status, startsAt, node)
            return current_alarm
        except:
            logging.error('Could not parse alertname')
    except:
        logging.error('Uncorrect json syntax in received alarm_description')
    return current_alarm


def generate_headers(response_prase):
    server = 'Server: python ' + sys.version.split('[')[0].strip() + ' ' +  sys.version.split('[')[1].strip().replace(']', '') + '\r\n'
    date = 'Date: ' + datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT') + '\r\n'
    connection = 'Connection: close\r\n\r\n'
    headers = ''.join([response_prase, server, date, connection])
    return headers


def check_config(config_path):
    try:
        with open(config_path, 'rb') as conf:
            config = json.load(conf, encoding='utf8')
        params = ['apihelper_proxy', 'grafana_token', 'grafana_url', 'bot_token', 'users_file']
        for param in params:
            try:
                config[param]
            except KeyError:
                logging.error(f'Param {param} is missed in config')
                return False
        for key in config.keys():
            if key not in params:
                logging.error(f'Unexpected param {key}')
                return False
        return config
    except json.decoder.JSONDecodeError:
        logging.error('Syntax error in config file')
        return False


def run(host, port, config):
    all_alarms = []
    bot = Bot(config)
    users = load_users(config['users_file'])
    users_reload_time = dt.today().timestamp()
    logging.info(f'Firs load users is: {users}')
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen()

    pid = os.fork()
    if pid != 0:
        bot.polling(none_stop=True, timeout=30)

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
            client_socket.sendall(generate_headers(response_prase).encode())
            current_alarm = make_current_alarm(response_prase, code, alarm_description)
            if current_alarm and not current_alarm in all_alarms:
                logging.info(f'current_alarm is: {current_alarm}')
                all_alarms.append(current_alarm)
                if os.path.getmtime(config['users_file']) > users_reload_time:
                    users = load_users(config['users_file'])
                    users_reload_time = dt.today().timestamp()
                    logging.info(f'Reload users is {users}')
                if len(users) > 0:
                    for user in users:
                        if users[user] in ['*', 'all', '\w', 'All', 'ALL']:
                            bot.send_message(user, alarm_description)
                        else:
                            if re.findall(r'%s' % users[user].lower(), current_alarm.alertname.lower()):
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
    config = check_config(opts.config)
    if config:
        logging.info(f'Use correct configuration file {opts.config}')
        try:
            run(opts.host, opts.port, config)
        except:
            logging.exception('Fatal unexpected error')
    else:
        logging.error(f'Used wrong configuration file')
