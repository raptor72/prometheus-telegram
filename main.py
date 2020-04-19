#!/usr/bin/python3

import os
import ast
import sys
import socket
import logging
import datetime
import subprocess
from bot_class import Bot, load_config
from optparse import OptionParser
from collections import namedtuple

Alarm = namedtuple('Alarm', 'alertname startsAt node')
DEFAULT_CONFIG = './default_config'
REQUEST_PARAMS = {
    'Host': 'Host',
    'User-Agent': 'User-Agent',
    'Content-Length': 'Content-Length',
    'Content-Type': 'Content-Type'
}

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
    try:
        url = parsed[1].split('?')[0]
        for i in request.split('\r\n'):
#            print('type:', i)
            try:
                # print(REQUEST_PARAMS[i.split(':')[0]])
                headers.update({REQUEST_PARAMS[i.split(':')[0]]: i.split(':')[1].strip()})
            except:
                continue
        print(headers)
        return method, url, headers
    except:
        return method, '', headers

def generate_response(request):
    method, url, headers = parse_request(request)
    if method not in ['POST']:
        return ('HTTP/1.1 405 Method not allowed\r\n', 405, None)
    if headers == {}:
        return ('HTTP/1.1 405 Can not parse headers format\r\n', 405, None)
    if not 'Alertmanager' in headers['User-Agent']:
        return ('HTTP/1.1 405 Unsupported sender\r\n', 405, None)
    if not 'json' in headers['Content-Type']:
        return ('HTTP/1.1 405 Unsupported Content-Type\r\n', 405, None)
    alarm_description = request.split('\r\n\r\n')[1]
    # print('alarm_description', alarm_description)
    return ('HTTP/1.1 200 OK\r\n', 200, alarm_description)

a = {"receiver":"tlg-bot","status":"firing","alerts":[{"status":"resolved","labels":{"alertname":"NetworkChange","severity":"Warning"},"annotations":{"description":"LABELES:  end of VALUE = 6 end has been change for more than 1 minute.","summary":"Network map[] change"},"startsAt":"2020-04-18T18:25:16.014462791+04:00","endsAt":"2020-04-18T19:15:46.014462791+04:00","generatorURL":"http://linuxmint-19-xfce:9090/graph?g0.expr=sum%28node_network_address_assign_type%29+%21%3D+3\u0026g0.tab=1","fingerprint":"ef8e10c065780d35"},{"status":"firing","labels":{"alertname":"NetworkChange","severity":"warning"},"annotations":{"description":"LABELS: map[] end of VALUE = 6 end has been change for more than 1 minute.","summary":"Network map[] change"},"startsAt":"2020-04-18T19:14:31.014462791+04:00","endsAt":"0001-01-01T00:00:00Z","generatorURL":"http://linuxmint-19-xfce:9090/graph?g0.expr=sum%28node_network_address_assign_type%29+%21%3D+3\u0026g0.tab=1","fingerprint":"4c3ea395fcf5a715"}],"groupLabels":{"alertname":"NetworkChange"},"commonLabels":{"alertname":"NetworkChange"},"commonAnnotations":{"summary":"Network map[] change"},"externalURL":"http://linuxmint-19-xfce:9093","version":"4","groupKey":"{}:{alertname=\"NetworkChange\"}"}
def make_current_alarm(alarm_description):
    d = {}
    try:
#        d.update(alarm_description)
        d = ast.literal_eval(alarm_description)
    except SyntaxError:
        logging.info("uncorrect json syntax")
    try:
        alertname = d['alerts'][0]['labels']['alertname']
    except:
        logging.info("could not parse alertname")
    startsAt = datetime.datetime.strptime(d['alerts'][0]['startsAt'][:26], '%Y-%m-%dT%H:%M:%S.%f').strftime('%Y-%m-%dT%H:%M:%S.%f')
    node = d['externalURL']
    current_alarm = Alarm(alertname, startsAt, node)
    return current_alarm


def run(port):
    all_alarms = []
    config = load_config(DEFAULT_CONFIG)
    #    print(config)
    bot = Bot(config["bot_token"], config["user_list"], config["command_list"], config["admin_id"])
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('127.0.0.1', port))
    server_socket.listen()

    pid = os.fork()
    if pid != 0:
        bot.polling(none_stop=True, timeout=30)
    else:
        while True:
            client_socket, addr = server_socket.accept()
            request = read_all(client_socket, maxbuff=2048)
            logging.info('request is: %s', request)
            logging.info('address is: %s', addr)
            if len(request.strip()) == 0:
                client_socket.close()
                continue
            if request:
                response_prase, code, alarm_description = generate_response(request.decode('utf-8'))
                client_socket.sendall((response_prase + str(code)).encode())
                print('alarm_description:', alarm_description)
#                bot.handle_text(alarm_description)
#                 current_alarm = make_current_alarm(alarm_description)
#                 if not current_alarm in all_alarms:
#                     all_alarms.append(current_alarm)
#                     bot.send_message(config["admin_id"], alarm_description)
            client_socket.close()
    server_socket.close()

if __name__ == '__main__':
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    logging.info('Starting server at %s' % opts.port)
    run(opts.port)
