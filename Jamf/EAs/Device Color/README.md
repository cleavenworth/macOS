# Device Color

We needed a way to fetch the physical device color to sync to our asset management system for more accurate hardware records.
Apple keeps a record of the color of a device within the DEP API, which Jamf's new uAPI has access to. This Script and EA are used together to fetch that color value from the API and store it as an EA for the device.

## Setup:

1. Create a JSS User with permissions to read DEP data, save the username and password for later.
2. Make note of the instance ID for your DEP configuration within the JSS.
3. Upload and Configure the Script
4. Create the EA

## Script Configuration:

Upload `get_dep_device_color_policy.py` to your JSS and add the below labels for the script parameters.

4. JSS Username
5. JSS Password
6. JSS URL
7. DEP Instance ID

## Policy Configuration:

1. Create a Policy with a Custom Event trigger: `get_device_color`
2. Add the `get_dep_device_color_policy.py` script to the policy.
3. Set the parameter values for the policy using the credentials you created for the JSS User, your JSS URL, and the DEP Instance ID.
4. Scope to All Computers, set to Ongoing

## EA Configuration:

1. Create a new EA, e.g. "Device Color"
2. Set to populate via Script
3. Use the provided `get_dep_device_color_EA.sh` script
