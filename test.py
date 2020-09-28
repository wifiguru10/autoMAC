#!/usr/bin/python3 -i

import meraki
import copy
import time

db = meraki.DashboardAPI(api_key=None, base_url='https://api.meraki.com/api/v1/', print_console=False)
org_id = '577586652210266696'

netid = 'L_577586652210275698'
serial = 'Q2MW-MW3X-LG3U'

tag_port_TARGET = 'AM:on'

devices_inscope = []
devices_inscope.append(serial)

ports_inscope = []
for d in devices_inscope:
    #ports = dashboard.switch_ports.getDeviceSwitchPorts(d['serial'])
    ports = db.switch.getDeviceSwitchPorts(serial)
    dname = 'Switch'
    portsIS = 0
    for p in ports:
       if p['tags'] is not None and tag_port_TARGET in p['tags']:
            newPort = p
            newPort['serial'] = serial
            newPort['netId'] = netid
            #ports_inscope.append(p)
            ports_inscope.append(newPort)
            portsIS += 1
            print(f'Checking switch ports:  Switch [{dname}] SN [{serial}] PortsInscope[{portsIS}]')
print("Ports Inscope:")
print(ports_inscope)

