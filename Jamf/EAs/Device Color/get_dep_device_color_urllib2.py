#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Fetches a device's color from the Jamf uAPI's DEP endpoint (this data is only
accessible there) and saves it to a local log to be read by an Extension Attribute.
The extension attribute itself can be a script that calls this policy with a custom event trigger.
This version uses standard libs only and is compatible with macOS' built-in Python.
"""

import urllib2
import base64
import json
import os
import sys

# Snippet to get device serial
import objc
from Foundation import NSBundle

IOKit_bundle = NSBundle.bundleWithIdentifier_('com.apple.framework.IOKit')

functions = [("IOServiceGetMatchingService", b"II@"),
             ("IOServiceMatching", b"@*"),
             ("IORegistryEntryCreateCFProperty", b"@I@@I"),
            ]

objc.loadBundleFunctions(IOKit_bundle, globals(), functions)

def io_key(keyname):
    return IORegistryEntryCreateCFProperty(IOServiceGetMatchingService(0, \
    IOServiceMatching("IOPlatformExpertDevice".encode("utf-8"))), keyname, None, 0)

def get_hardware_serial():
    return io_key("IOPlatformSerialNumber".encode("utf-8"))

#### Jamf API credentials, supplied via Paramter values within the policy.
#### Jamf's own https://github.com/jamf/Encrypted-Script-Parameters is recommended
#### to ensure the API credentials remain secure, as is creating a unique JSS user
#### with permissions only to read DEP data.
username = sys.argv[4]
password = sys.argv[5]
JamfUrl = sys.argv[6]
DeviceEnrollmentInstanceId = sys.argv[7]
DeviceSerial = get_hardware_serial()

#### Jamf API Info DO NOT CHANGE BELOW THIS LINE
GetTokenEndpoint = JamfUrl + "/uapi/auth/tokens"
InvalidateTokenEndpoint = JamfUrl + "/uapi/auth/invalidateToken"
DeviceEnrollmentEndpoint = JamfUrl + \
"/uapi/v1/device-enrollment/{}/devices".format(DeviceEnrollmentInstanceId)

def create_auth_token():
    auth_request = urllib2.Request(GetTokenEndpoint)
    auth_string = base64.b64encode('%s:%s' % (username, password)).replace('\n', '')
    auth_request.add_header('Authorization', 'Basic %s' % auth_string)
    auth_request.get_method = lambda: 'POST'
    request = urllib2.urlopen(auth_request)
    data = request.read()
    token = json.loads(data.replace('\n', ''))['token']
    return token

def expire_auth_token(token):
    auth_request = urllib2.Request(InvalidateTokenEndpoint)
    auth_request.add_header('Authorization', 'Bearer %s' % token)
    auth_request.get_method = lambda: 'POST'
    request = urllib2.urlopen(auth_request)
    result = request.getcode()
    if result == 200:
        return
    print("Unable to expire token", result)

def get_dep_devices(token):
    dep_request = urllib2.Request(DeviceEnrollmentEndpoint)
    dep_request.add_header('Authorization', 'Bearer %s' % token)
    dep_request.get_method = lambda: 'GET'
    request = urllib2.urlopen(dep_request)
    data = request.read()
    dep_devices = json.loads(data.replace('\n', ''))
    return dep_devices

def find_this_computer(devices_json, serialnumber):
    for computer in devices_json['results']:
        if serialnumber in computer['serialNumber']:
            this_computer = computer
    return this_computer

def get_color(device_json):
    color = device_json['color'].title()
    return color

def save_color_to_log(color, serialnumber):
    log_filename = "{}-color.log".format(serialnumber)
    log_location = os.path.join('/var/log/', log_filename)
    log_file = open(log_location, 'w+')
    log_file.write(color)
    log_file.close()

if __name__ == "__main__":
    AUTHTOKEN = create_auth_token()
    THISMAC = find_this_computer(get_dep_devices(AUTHTOKEN), DeviceSerial)
    THECOLOR = get_color(THISMAC)
    save_color_to_log(THECOLOR, DeviceSerial)
    expire_auth_token(AUTHTOKEN)
