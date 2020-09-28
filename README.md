# Meraki autoMAC
Meraki autoMAC - allows you to automatically configure the switch ports on a MS network based on historical cisco switch config(show run and show mac address-table) or device profiles (OUI/CDP/LLDP/MAC/Vendor). Think of it like API based Secure-Connect. Works on any switch type.

![autoMAC RULES](images/autoMAC.PNG)


# Steps
1. place config files in local directory (raw output from 'show run' on the ASA)
2. Create a new MX network in the Meraki Dashboard
3. Enable "Use VLANs" under "Addressing & Vlans" (it'll error out if you don't do this!)
4. Create interfaces (vlan, ip and subnet) in that new network (these should match interfaces VLAN-ID in the config file)
5. For step#4, the IP/subnets do not have to match, just the VLAN-ID. The script will auto-map the new IP/subnet to the ruleset
6. Edit "acl_list.txt" this file should contain the names of every ACL rule you want to process
7. RUN THIS ON A TEST NETWORK FIRST! This re-writes ALL the rules and anything currently in the rules will be lost.
8. Run the commandline "python3 mx_import.py -k \<key\> -o \<org\> -n \<networkID\> -c command \<ASA CONFIG FILE\>"
  -commands supported "write", "clear" and "test". Test is default. Clear will wipe the FW rules.
9. After the script runs, validate the rules have ported correctly. The comments section will hold the original ACL rule to compare

# Requirements
1. python 3.x
2. meraki SDK v1 or later for python (https://developer.cisco.com/meraki/api/#/python/getting-started)
3. install python packages ('pip3 install -r requirements.txt')

# Known caveats:
-test it first

# Example Output
![output](images/output.png)
