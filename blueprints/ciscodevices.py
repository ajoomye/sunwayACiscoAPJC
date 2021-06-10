'''
IMPORTING NECESSARY LIBRARIES
'''

import requests, matplotlib.pyplot as plt
from flask import Blueprint, render_template, redirect, request
import json
from variables import *
from netmiko import ConnectHandler
import json, threading, time

ciscodevices = Blueprint("ciscodevices", __name__, static_folder="static", template_folder="templates")

#Getting meraki devices and ios devices details from the variables.py
merakideviceslist = merakidevices
iosdeviceslist = iosdevices

'''
CODE FOR WHEN LOADING THE CISCODEVICES PAGE
'''
@ciscodevices.route('/', methods=['GET','POST'])
def list1():
    global deviceDetails
    deviceDetails = []

    ####
    # Getting Meraki devices details for display using Meraki API
    ####
    for merakidevice in merakideviceslist:
        for serial in merakidevice['merakiserials']:
            try:
                url = f"https://api.meraki.com/api/v0/devices/{serial}/switchPorts"
                payload = {}
                headers = {
                    "X-Cisco-Meraki-API-Key": merakidevice['merakiapikey']
                }

                response = requests.request('GET', url, headers=headers, data = payload)
                responses = response.json()

                for i in responses:
                    switch = serial
                    devicenumber = i['number']
                    devicename = i['name']
                    deviceenable = i['enabled']
                    if deviceenable == True:
                        onoff = "On"
                    elif deviceenable == False:
                        onoff = "Off"
                    port = f"{switch}-{devicenumber}"
                    deviceDetails.append([switch, devicenumber, devicename, onoff, port])
            except:
                pass

    ####
    # Getting ios devices details for display using Netmiko
    ####
    for device in iosdeviceslist:
        try:
            print(device)
            connection = ConnectHandler(**device)
            connection.enable()
            interfaces = connection.send_command('sh int status', use_textfsm=True)
            for i in interfaces:
                if i['status'] == "connected":
                    onoff = "On"
                else:
                    onoff = "Off"
                port = f"{switch}-{i['port']}"
                portlist = [device['host'],i['port'],i['name'],onoff, port]
                deviceDetails.append(portlist)
        except:
            pass


    headings = ("Switch","Port Number", "Device name", "Status","On/Off")

    return render_template('ciscodevices.html', headings=headings, data=deviceDetails)

'''
CODE FOR TURNING INDIVIDUAL PORTS ON AND OFF
'''
@ciscodevices.route('/shutports/', methods=['POST'])
def shutports():
    print(deviceDetails)
    #Getting details from the checkboxes:
    checkoutput = request.form.getlist('ondevices')
    print(checkoutput)

    #Setting lists for devices to turn on/off:
    toturnon=[]
    toturnoff=[]

    for i in deviceDetails:
        if i[3] == 'Off' and i[4] in checkoutput:
            toturnon.append(i)
        if i[3] == 'On' and i[4] not in checkoutput:
            toturnoff.append(i)

    ####
    # Turning selected Meraki devices on/off using Meraki API
    ####

    for merakidevice in merakideviceslist:
        for serial in merakidevice['merakiserials']:
            def shutportmeraki(port,enabled):

                print(port)
                url = f"https://api.meraki.com/api/v0/devices/{serial}/switchPorts/{port}?enabled={enabled}"

                payload = json.dumps({
                "enabled": enabled
                })
                headers = {
                'X-Cisco-Meraki-API-Key': merakidevice['merakiapikey'],
                'Content-Type': 'application/json'
                }

                response = requests.request("PUT", url, headers=headers, data=payload)

                print(response.text)



            for i in toturnon:
                if i[0] == serial:
                    shutportmeraki(i[1],True)

            for i in toturnoff:
                if i[0] == serial:
                    shutportmeraki(i[1],False)

    ####
    # Turning selected IOS devices on/off using Netmiko
    ####
    for device in iosdevices:
        def shutios(portlist, enabled):
            try:
                connection = ConnectHandler(**device)
                connection.enable()
                print('Connection Enabled')
                for i in portlist:
                    command = f'int {i}'
                    if enabled == False:
                        output = connection.send_config_set([command, 'shut'])
                        print(output)
                    elif enabled == True:
                        output = connection.send_config_set([command, 'no shut'])
                        print(output)
            except:
                pass

        deviceon = []
        for i in toturnon:
            if i[0] == device['host']:
                deviceon.append(i[1])
        shutios(deviceon,True)

        deviceoff=[]
        for i in toturnoff:
            if i[0] == device['host']:
                deviceoff.append(i[1])
        shutios(deviceoff,False)


    return list1()
