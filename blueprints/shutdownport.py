#PAGE WHEN TURNING ON/OFF PORTS AT SELECTED TIMES 

'''
IMPORTING NECESSARY LIBRARIES
'''
import requests, json, time, schedule
from flask import Blueprint, render_template, redirect, request
from variables import *
from netmiko import ConnectHandler


def getmerakidetailstoshut(merakidevices, enabled):
    #Message to be sent using Webex API
    if enabled == True:
        message = "your selected devices have been turned on"
    elif enabled == False:
        message = "your selected devices have been turned off"
    
    #Loading portlists.json file to obtain if port has been set to turn on/off at set time.
    device = open('portlists.json','r')
    readdevice = json.load(device)
    device.close()

    ####
    # Turning set Meraki devices on/off using Meraki API
    ####
    for merakidevice in merakidevices:
        for serial in merakidevice['merakiserials']:
            print(serial)
            portIds = readdevice[serial]
            def shutportmeraki(portIds,enabled):
                for port in portIds:
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
            
            shutportmeraki(portIds,enabled)
    
    ####
    # Turning set IOS devices on/off using Netmiko
    ####
    for device in iosdevices:
        try:
            portlist=readdevice[device['host']]
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

    ####
    #Webex API to send message. The room ID and Authorization is for Abdurraheem's account and his shutport bot.
    ####
    def webexmessage(message):
        url = "https://webexapis.com/v1/messages"

        payload = json.dumps({
        "roomId": "Y2lzY29zcGFyazovL3VzL1JPT00vZDg1MmQ1ZDAtYmU1Zi0xMWViLWE1YzItM2ZmMTcyMjlhZDQy",
        "text": message
        })
        headers = {
        'Authorization': 'Bearer MTA2MzRlNTEtNDNiNi00NDlmLTllZmMtMDI1ZDJjMzE1ZDMyY2RjZWY4MWQtODU0_PF84_ebdf3b62-c327-4af2-8733-10d8711bb8cd ',
        'Content-type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)


    webexmessage(message)
