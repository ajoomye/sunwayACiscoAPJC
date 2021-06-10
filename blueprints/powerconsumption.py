'''
IMPORTING NECESSARY LIBRARIES
'''

import requests, matplotlib.pyplot as plt
from flask import Blueprint, render_template, redirect
import json
from variables import *

powerconsumption = Blueprint("powerconsumption", __name__, static_folder="static", template_folder="templates")


####
#GETTING DETAILS ABOUT POWER CONSUMPTION FROM THE MERAKI SWITCHES USING MERAKI API
####
@powerconsumption.route('/')
def list():
    portDetails = []
    for merakidevice in merakidevices:
        for serial in merakidevice['merakiserials']:
            url = f"https://api.meraki.com/api/v1/devices/{serial}/switch/ports/statuses"
            payload = {}
            headers = {
                "X-Cisco-Meraki-API-Key": merakidevice['merakiapikey']
            }

            response = requests.request('GET', url, headers=headers, data = payload)
            responses = response.json()

            for i in responses:
                serial=serial
                portId = i['portId']
                portstat = i['status']

                try:
                    power = i['powerUsageInWh']
                    powerconsume = power
                except KeyError:
                    powerconsume = 'N/A'

                portDetails.append([serial,portId, portstat, powerconsume])

    headings = ("Switch", "Port ID", "Status", "Power Usage (Wh)")


    return render_template('powerconsumption.html', headings=headings, data=portDetails)
