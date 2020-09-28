# Meraki autoMAC
Meraki autoMAC - allows you to automatically configure the switch ports on a MS network based on historical cisco switch config(show run and show mac address-table) or device profiles (OUI/CDP/LLDP/MAC/Vendor). Think of it like API based Secure-Connect. Works on any switch type.

![autoMAC Output](images/autoMAC.png)


# Steps
1. place config files in local directory 'cisco/' (raw output from 'show run' and 'show mac address-table' in a "<IP> <NAME>.log" file format)
2. Configure the ORG_ID in 'autoMAC.py' to match the org your configuring
3. TAG your switch Network with "autoMAC" tag
4. TAG your switches in the Network with "autoMAC" (not tagging them will exclude them)
5. TAG your switch ports with "AM:on" to allow switch port configuration (requires them to be an access port, not TRUNK!)
6. (optional) TAG your switch ports with "AM:auto" as well as "AM:on" to have it perpetually configure port on change, otherwise it'll be one-time config
7. If you have your network, switches and ports tagged, run the script!
  
# Requirements
1. python 3.x
2. meraki SDK v1 or later for python (https://developer.cisco.com/meraki/api/#/python/getting-started)
3. install python packages ('pip3 install -r requirements.txt')

# Known caveats:
-test it first

# Example Output
![output](images/output.png)
