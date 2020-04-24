import pytest
from collections import namedtuple
from main import *
from bot import *


@pytest.fixture
def write_empty_config(tmpdir):
    config = tmpdir.join('empty_config.txt')
    return config


@pytest.mark.parametrize("arguments", [
    {"a":"1"},
    {"b":"2", "b":"2", "b":"2", "b":"2", "b":"2"},

    # too shot config
    '''{"apihelper_proxy": {"https":"socks5://tlg-user-id:password@proxy:port"},
    "grafana_token": {"Authorization": "Bearer some_text"},
    "grafana_url": "http://127.0.0.1:3000",
    "users_file": "users"}''',

    # too long config
    '''{"apihelper_proxy": "test_value",
    "grafana_token": "test_value",
    "grafana_url": "test_value",
    "bot_token": "test_value",
    "users_file": "test_value",
    "one_more_key": "test_value"}''',

    # " is missed
    '''{"apihelper_proxy": {"https":"socks5://tlg-user-id:password@proxy:port"},
    "grafana_token": {"Authorization": "Bearer some_text"},
    "grafana_url": "http://127.0.0.1:3000",
    "bot_token": "12345678:ToKen,  
    "users_file": "users"}''',

    # " bad json
    '''{"apihelper_proxy": "https":"socks5://tlg-user-id:password@proxy:port"},
    "grafana_token": {"Authorization": "Bearer some_text"},
    "grafana_url": "http://127.0.0.1:3000",
    "bot_token": "12345678:ToKen",
    "users_file": "users"}'''
])
def test_uncorrect_many_length_config(arguments, write_empty_config):
    conf = write_empty_config
    conf.write(arguments)
    config = check_config(conf)
    assert config is False


@pytest.mark.parametrize("arguments", [
                   '''{"apihelper_proxy": {"https":"socks5://tlg-user-id:password@proxy:port"},
                   "grafana_token": {"Authorization": "Bearer some_text"},
                   "grafana_url": "http://127.0.0.1:3000",
                   "bot_token": "12345678:ToKen",
                   "users_file": "users"}''',

                   '''{"apihelper_proxy": "test_value",
                   "grafana_token": "test_value",
                   "grafana_url": "test_value",
                   "bot_token": "test_value",
                   "users_file": "test_value"}'''
])
def test_correct_many_config(arguments, write_empty_config):
    conf = write_empty_config
    conf.write(arguments)
    config = check_config(conf)
    assert config is True


@pytest.mark.parametrize(
    "arguments",
    [
# original request
        """POST / HTTP/1.1\r\nHost: 127.0.0.1:8080\r\nUser-Agent: Alertmanager/0.20.0\r\nContent-Length: 1128\r\nContent-Type:
        application/json\r\n\r\n{"receiver":"tlg-bot","status":"firing","alerts":[{"status":"firing",
        "labels":{"alertname":"LoadAverage1minutes","instance":"localhost:9100","job":"node","severity":"warning"},
        "annotations":{"description":"Load is high \\n  VALUE = 2.295\\n  LABELS: map[instance:localhost:9100 job:node]",
        "summary":"Load average is high for 1 minutes (instance localhost:9100)"},"startsAt":"2020-04-23T17:28:01.014462791+04:00",
        "endsAt":"0001-01-01T00:00:00Z","generatorURL":"http://linuxmint-19-xfce:9090/graph?g0.expr=node_load1+%2F+count+by%28insta
        nce%2C+job%29+%28node_cpu_seconds_total%7Bmode%3D%22idle%22%7D%29+%3E%3D+0.95\\u0026g0.tab=1","fingerprint":"4479a96add809b9d"}],
        "groupLabels":{"alertname":"LoadAverage1minutes"},"commonLabels":{"alertname":"LoadAverage1minutes","instance":"localhost:9100",
        "job":"node","severity":"warning"},"commonAnnotations":{"description":"Load is high \\n  VALUE = 2.295\\n  LABELS: map[instance:
        localhost:9100 job:node]","summary":"Load average is high for 1 minutes (instance localhost:9100)"},
        "externalURL":"http://linuxmint-19-xfce:9093","version":"4","groupKey":"{}:{alertname=\\"LoadAverage1minutes\\"}"}\n""",
# minimal requirements
    """POST / HTTP/1.1\r\nUser-Agent: Alertmanager\r\nContent-Type:
       application/json\r\n\r\n{"receiver":"tlg-bot")
    """
])
def test_parse_correct_request(arguments):
    response_prase, code, alarm_description = generate_response(arguments)
    assert 'HTTP/1.1 200 OK' in response_prase
    assert code == 200
    assert alarm_description is not None