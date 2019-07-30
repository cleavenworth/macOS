#!/bin/bash

/usr/local/bin/jamf policy -event get_device_color

SERIAL=$(system_profiler SPHardwareDataType | grep 'Serial Number (system)' | awk '{print $NF}')

COLOR=$(cat "/var/log/$SERIAL-color.log")

echo "<result>$COLOR</result>"
