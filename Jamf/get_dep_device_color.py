#!/usr/bin/env python
"""
Fetches a device's color from the Jamf uAPI's DEP endpoint (this data is only
accessible there) and saves it to a local log to be read by an Extension Attribute.
This version is partially compelte and uses the requests module for easier API calls.
"""

import requests
import json

#### Test Values
username = ""
password = ""
DeviceSerial = ""

#### JSS Info
JamfUrl = ""
DeviceEnrollmentInstanceId = ""
GetTokenEndpoint = JamfUrl + "/uapi/auth/tokens"
InvalidateTokenEndpoint = JamfUrl + "/uapi/auth/invalidateToken"
DeviceEnrollmentEndpoint = JamfUrl + \
"/uapi/v1/device-enrollment/{}/devices".format(DeviceEnrollmentInstanceId)

def create_auth_token():
    token = requests.post(GetTokenEndpoint, auth=(username, password))
    # if token.status_code != "200":
    #     return "Bad Token"
    return token.json()['token']

def expire_auth_token(token):
    expire_token_result = requests.post(InvalidateTokenEndpoint, \
    headers=token)
    return expire_token_result.status

def get_dep_devices(token):
    dep_devices = requests.get(DeviceEnrollmentEndpoint, headers=token).json()
    return dep_devices

def find_this_computer(devices_json, serialnumber):
    for computer in devices_json['results']:
        if serialnumber in computer['serialNumber']:
            this_computer = computer
    return this_computer

def get_color(device_json):
    color = device_json['color'].title()
    return color

if __name__ == "__main__":
    AUTHTOKEN = {"Authorization": "Bearer " + create_auth_token()}
    THISMAC = find_this_computer(get_dep_devices(AUTHTOKEN), DeviceSerial)
    THECOLOR = get_color(THISMAC)
    print(THECOLOR)
