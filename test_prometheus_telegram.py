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