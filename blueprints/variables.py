#PYTHON FILE TO GET DEVICES DETAILS USING JSON FROM THE VARIABLES.TXT FILES

import json
global merakidevices
global switches
global timeon
global timeoff
global iosswitch
global iosdevices

with open('variables.txt') as variablefile:
    variables = json.load(variablefile)
    merakidevices = variables['merakidevices']
    timeon = variables['timeon']
    timeoff = variables['timeoff']
    iosdevices = variables['iosdevices']

iosswitch = {'device_type': 'cisco_ios', 'host': '198.18.134.11', 'port': 22,
              'username': 'admin',
              'password': 'C1sco12345',
              'verbose': True}
