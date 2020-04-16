#!/usr/bin/python3

import os
import sys
import socket
import logging
import datetime
from optparse import OptionParser

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

def run(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('127.0.0.1', port))
    server_socket.listen()
    while True:
        client_socket, addr = server_socket.accept()
        request = read_all(client_socket, maxbuff=2048)
        if len(request.strip()) == 0:
            client_socket.close()
            continue
        if request:
            response = generate_response(request.decode('utf-8'))
            print('response:', response)
        logging.info('request is: %s', request)
        logging.info('address is: %s', addr)
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
