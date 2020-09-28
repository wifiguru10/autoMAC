#!/usr/bin/python3

import csv
import meraki
import time
from datetime import datetime

import csv

f='paris/Meraki_Switch_Assignment2.csv'
netid = 'N_754352937584559035'
orgid = '648464'

results = []
with open(f) as csvfile:
        reader = csv.reader(csvfile) # change contents to floats
        for row in reader: # each row is a list
            results.append(row)

print(results)

db = meraki.DashboardAPI(api_key=None, base_url='https://api.meraki.com/api/v1/', print_console=False)

serials = []
for r in results:
    serials.append(r[1])

print(serials)

#db.devices.claimNetworkDevices(netid,serials=serials)

port = {'name': None,
 'tags': ['AM:on'],
 'enabled': True,
 'poeEnabled': True,
 'type': 'access',
 'vlan': 1,
 'voiceVlan': None,
 'allowedVlans': 'all',
 'isolationEnabled': False,
 'rstpEnabled': True,
 'stpGuard': 'disabled',
 'linkNegotiation': 'Auto negotiate',
 'portScheduleId': None,
 'udld': 'Alert only',
 'accessPolicyType': 'Open'}

trunk = { 'name': None,
 'tags': ['uplink'],
 'enabled': True,
 'poeEnabled': False,
 'type': 'trunk',
 'vlan': 500,
 'voiceVlan': None,
 'allowedVlans': 'all',
 'isolationEnabled': False,
 'rstpEnabled': True,
 'stpGuard': 'disabled',
 'linkNegotiation': 'Auto negotiate',
 'portScheduleId': None,
 'udld': 'Alert only'}


updateName = False
if updateName:
    for r in results:
        serial = r[1]
        name = r[4]
        db.devices.updateDevice(serial,name=name)
        print(f'Set Name[{name}] on Serial[{serial}]')



#Iterate through all the devices in network and default any interface that has been tagged with 'autoMAC'
devices = db.networks.getNetworkDevices(netid)

for d in devices:
    dname = d['name']
    tags = d['tags']
    if 'autoMAC' in tags:
        serial = d['serial'] 
        for count in range(1,49): # 1..48
           p = db.switch.updateDeviceSwitchPort(serial,count, **port) 
           print(p) 
        for count in range(49,53): # 49,50,51,52
           p = db.switch.updateDeviceSwitchPort(serial,count, **trunk)
           print(p)
    else:
        print(f'Excluding switch {dname}')
