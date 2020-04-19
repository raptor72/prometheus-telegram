#!/usr/bin/python3

# -*- coding: utf-8 -*-

import requests
import time
import os
import argparse
import json
import glob
from config import *

def get_grafana_dashboards(g_url, g_token):
    dashboards_array = []
#    headers = {'Authorization': str('Bearer ' + g_token), 'Content-type': 'application/json'}
    headers = {'Content-type': 'application/json'}
    headers.update(g_token)
    get_data_req = requests.get(g_url + '/api/search?query=&', headers=headers)
    pars_json = json.loads(get_data_req.text)
    for dash in pars_json:
        dashboards_array.append(dash['uri'][3::])
    print(dashboards_array)
    return dashboards_array

#get_grafana_dashboards(grafana_url, grafana_token)


def export_grafana_dashboards(g_token, g_url, e_dash):
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

print(export_grafana_dashboards(grafana_token, grafana_url, 'prometheus-2-0-stats'))
panels = export_grafana_dashboards(grafana_token, grafana_url, 'prometheus-2-0-stats')

panels_title = []
for i in panels:
    print(i)
#    panels_title.append(i)

#print(panels_title)