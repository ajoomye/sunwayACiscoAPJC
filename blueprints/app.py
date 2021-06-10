'''
IMPORTING NECESSARY LIBRARIES
'''
import requests, json, time, schedule,os
from flask import Flask, render_template, request, redirect
from datetime import datetime
from powerconsumption import powerconsumption
from ciscodevices import ciscodevices
from settings import settings
from variables import *
from shutdownport import *
from threading import Thread

'''
CREATING INSTANCE AND REGISTER FLASK BLUEPRINTS
'''

app = Flask(__name__, template_folder='../templates')
app.register_blueprint(powerconsumption, url_prefix="/powerconsumption")
app.register_blueprint(ciscodevices, url_prefix="/ciscodevices")
app.register_blueprint(settings, url_prefix="/settings")

'''
TO GET DETAILS FOR THE TABLES IN HOME PAGE AND DEVICES
'''
def getmerakidetails():
    global alldevices
    alldevices = []
    for merakidevice in merakidevices:
        for serial in merakidevice['merakiserials']:
            try:
                url = f"https://api.meraki.com/api/v0/devices/{serial}/switchPorts"
                payload = {}
                headers = {
                    "X-Cisco-Meraki-API-Key": merakidevice['merakiapikey']
                }

                response = requests.request('GET', url, headers=headers, data = payload)
                responses = response.json()
                alldevices.append(responses)
            except:
                pass
    return alldevices


'''
FOR INDEX PAGE
'''

#####
# FOR THE DEVICES ON TABLE SHOWING ONLY TURNED ON DEVICES
#####
@app.route('/')
def index():
    global deviceSerial
    deviceSerial = []
    for switch in getmerakidetails():
        for i in switch:
            if i['enabled'] == True:
                devicename = i['name']
                deviceSerial.append(devicename)
    for device in iosdevices:
        try:    
            print(device)
            connection = ConnectHandler(**device)
            connection.enable()
            interfaces = connection.send_command('sh int status', use_textfsm=True)
            for i in interfaces:
                if i['status'] == "connected":
                    devicestatus = f"{device['host']}-{i['port']}"
                    deviceSerial.append(devicestatus)
        except:
            pass

    return render_template('ciscoindex.html', data=deviceSerial, timeon=timeon, timeoff=timeoff)



#####
# TO SET SCHEDULE FOR THE DEVICES
#####    
@app.route('/', methods=['POST'])
def my_form_post():
    global timeon
    global timeoff
    timeon = request.form.get('timeon')
    print(timeon)
    timeoff = request.form.get('timeoff')
    print(timeoff)
    variables['timeon'] = timeon
    variables['timeoff'] = timeoff

    a_file = open("variables.txt", "w")
    json.dump(variables, a_file)
    a_file.close()

    datatime = [timeon, timeoff]

    
    
    schedule.every().day.at(timeon).do(getmerakidetailstoshut, merakidevices=merakidevices, enabled = True)
    schedule.every().day.at(timeoff).do(getmerakidetailstoshut,merakidevices=merakidevices, enabled = False)


    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

