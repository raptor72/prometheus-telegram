#!/usr/bin/python3

import logging
import datetime
from collections import namedtuple
Alarm = namedtuple('Alarm', 'alertname startsAt node')

def configure_logging(log_filename):
    logging.basicConfig(format = u'[%(asctime)s] %(levelname).1s %(message)s', filename=log_filename, datefmt='%Y.%m.%d %H:%M:%S',
                    level=logging.INFO
                    )

a = {"receiver":"tlg-bot","status":"firing","alerts":[{"status":"firing","labels":{"alertname":"NetworkChange","severity":"Warning"},"annotations":{"description":"LABELES:  end of VALUE = 6 end has been change for more than 1 minute.","summary":"Network map[] change"},"startsAt":"2020-04-18T18:25:16.014462791+04:00","endsAt":"0001-01-01T00:00:00Z","generatorURL":"http://linuxmint-19-xfce:9090/graph?g0.expr=sum%28node_network_address_assign_type%29+%21%3D+3\u0026g0.tab=1","fingerprint":"ef8e10c065780d35"}],"groupLabels":{"alertname":"NetworkChange"},"commonLabels":{"alertname":"NetworkChange","severity":"Warning"},"commonAnnotations":{"description":"LABELES:  end of VALUE = 6 end has been change for more than 1 minute.","summary":"Network map[] change"},"externalURL":"http://linuxmint-19-xfce:9093","version":"4","groupKey":"{}:{alertname=\"NetworkChange\"}"}
def make_current_alarm(alarm_description):
#Alarm = namedtuple('Alarm', 'alertname startsAt node')
    d = {}
    try:
        d.update(alarm_description)
    except SyntaxError:
        logging.info("uncorrect json syntax")
    try:
        alertname = d['alerts'][0]['labels']['alertname']
    except:
        logging.info("could not parse alertname")
#    startsAt = datetime.datetime.strptime(d['alerts'][0]['startsAt'], '%Y-%m-%dT%H:%M:%S.%f%%%%Z:00')
    startsAt = datetime.datetime.strptime(d['alerts'][0]['startsAt'][:26], '%Y-%m-%dT%H:%M:%S.%f').strftime('%Y-%m-%dT%H:%M:%S.%f')
#    startsAt = d['alerts'][0]['startsAt'][:26]
    node = d['externalURL']
#    return alertname, startsAt, node
    current_alarm = Alarm(alertname, startsAt, node)
    return current_alarm

print(make_alarmtuple(a))

