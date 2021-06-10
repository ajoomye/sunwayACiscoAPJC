'''
IMPORTING NECESSARY LIBRARIES
'''

import requests, matplotlib.pyplot as plt
from flask import Blueprint, render_template, redirect, request, Flask
import json
from variables import *
from netmiko import ConnectHandler

settings = Blueprint("settings", __name__, static_folder="static", template_folder="templates")

#Getting meraki devices and ios devices details from the variables.py
merakideviceslist = merakidevices
iosdeviceslist = iosdevices

'''
GETTING DETAILS FOR SET SCHEDULE LIST TABLE
'''
@settings.route('/', methods=['GET','POST'])
def displaysetting():
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
                    with open('portlists.json') as portlists:
                        device = json.load(portlists)
                        ports = device[switch]
                    if devicenumber in ports:
                        inschedule = "in"
                    else:
                        inschedule = "out"
                    port = f"{switch}-{devicenumber}"
                    deviceDetails.append([switch, devicenumber, devicename, inschedule, port])
            except:
                pass

    ####
    # Getting ios devices details for display using Netmiko
    ####
    for thisiosdevice in iosdeviceslist:
        try:
            print(thisiosdevice)
            connection = ConnectHandler(**thisiosdevice)
            connection.enable()
            switch = thisiosdevice['host']
            interfaces = connection.send_command('sh int status', use_textfsm=True)
            for i in interfaces:
                with open('portlists.json') as portlists:
                    device = json.load(portlists)
                    ports = device[switch]
                if i['port'] in device[switch]:
                    inschedule = "in"
                else:
                    inschedule = "out"
                port = f"{switch}-{i['port']}"
                portlist = [switch,i['port'], i['name'], inschedule, port]
                deviceDetails.append(portlist)
        except:
            pass


    headings = ("Switch","Port Number", "Device name", "In Schedule")

    return render_template('settings.html', headings=headings, data=deviceDetails)


'''
ADDING NEW MERAKI SWITCH
'''
@settings.route('/meraki/', methods=['POST'])
def addmerakisetting():
    newmerakiapikey = request.form.get('merakiapikey')
    switchserial = request.form.get('serial')
    print(newmerakiapikey)
    newlist = merakidevices
    print(newlist)
    newkey = {"merakiapikey": newmerakiapikey, "merakiserials": [switchserial]}
    newlist.append(newkey)
    variables['merakidevices'] = newlist
    a_file = open("variables.txt", "w")
    json.dump(variables, a_file)
    a_file.close()
    device = open('portlists.json','r')
    readdevice = json.load(device)
    device.close()
    print(readdevice)
    newdict = {switchserial: []}
    readdevice.update(newdict)
    print(readdevice)
    device = open('portlists.json','w')
    json.dump(readdevice, device)
    print(readdevice)
    device.close()

    print(merakidevices)

    return displaysetting()


'''
ADDING NEW CISCO IOS SWITCH
'''
@settings.route('/iosipadd/', methods=['POST'])
def showip():
    iosipadd = request.form.get('iosipadd')
    username = request.form.get('username')
    password = request.form.get('password')
    secret = request.form.get('secret')
    newlist = iosdevices
    print(newlist)
    if secret == '':
        newiosdevice = {'device_type': 'cisco_ios', 'host': iosipadd, 'port': 22,
              'username': username,
              'password': password,
              'verbose': True}
    else:
        newiosdevice = {'device_type': 'cisco_ios', 'host': iosipadd, 'port': 22,
              'username': username,
              'password': password,
              'secret': secret,
              'verbose': True}
    newlist.append(newiosdevice)
    variables['iosdevices'] = newlist
    a_file = open("variables.txt", "w")
    json.dump(variables, a_file)
    a_file.close()
    device = open('portlists.json','r')
    readdevice = json.load(device)
    device.close()
    print(readdevice)
    newdict = {iosipadd: []}
    readdevice.update(newdict)
    print(readdevice)
    device = open('portlists.json','w')
    json.dump(readdevice, device)
    print(readdevice)
    device.close()

    return displaysetting()

'''
EDITING THE LIST OF DEVICES IN TO TURN ON/OFF AT SET TIME
'''
@settings.route('/addschedule/', methods=['POST'])
def addschedule():
    print(deviceDetails)
    checkoutput = request.form.getlist('addtoschedule')
    print(checkoutput)
    addtoschedule=[]
    remove=[]
    for i in deviceDetails:
        if i[3] == 'out' and i[4] in checkoutput:
            device = open('portlists.json','r')
            readdevice = json.load(device)
            device.close()
            print(readdevice)
            readdevice[i[0]].append(i[1])
            print(readdevice)
            device = open('portlists.json','w')
            json.dump(readdevice, device)
            print(readdevice)
            device.close()
        if i[3] == 'in' and i[4] not in checkoutput:
            device = open('portlists.json','r')
            readdevice = json.load(device)
            device.close()
            print(readdevice)
            readdevice[i[0]].remove(i[1])
            print(readdevice)
            device = open('portlists.json','w')
            json.dump(readdevice, device)
            print(readdevice)
            device.close()

    return displaysetting()
