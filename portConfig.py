#!/usr/bin/python3

from switchDB import bcolors
import copy
from datetime import datetime

class portConfig:

    ports = {}
    unique = []
    
    trunkDefault = {'portId': '25', 'name': None, 'tags': [], 'enabled': True, 'poeEnabled': False, 'type': 'trunk', 'vlan': 1, 'voiceVlan': None, 'allowedVlans': 'all', 'isolationEnabled': False, 'rstpEnabled': True, 'stpGuard': 'disabled', 'linkNegotiation': 'Auto negotiate', 'portScheduleId': None, 'udld': 'Alert only'}

    APtrunk = {'portId': '25', 'name': 'Meraki AP', 'tags': ['AP', 'AM:profiled'], 'enabled': True, 'poeEnabled': True, 'type': 'trunk', 'vlan': 111, 'voiceVlan': None, 'allowedVlans': 'all', 'isolationEnabled': False, 'rstpEnabled': True, 'stpGuard': 'BPDU guard', 'linkNegotiation': 'Auto negotiate', 'portScheduleId': None, 'udld': 'Alert only'}

    accessDefault = {'portId': '1', 'name': '', 'tags': ['AM:profiled'], 'enabled': True, 'poeEnabled': True, 'type': 'access', 'vlan': 6, 'voiceVlan': None, 'allowedVlans': 'all', 'isolationEnabled': False, 'rstpEnabled': False, 'stpGuard': 'disabled', 'linkNegotiation': 'Auto negotiate', 'portScheduleId': None, 'udld': 'Alert only', 'accessPolicyType': 'Open'}
 
    accessBlock = {'portId': '1', 'name': 'BLOCKED CLIENT', 'tags': ['AM:profiled', 'AM:blocked'], 'enabled': True, 'poeEnabled': True, 'type': 'access', 'vlan': 999, 'voiceVlan': None, 'allowedVlans': 'all', 'isolationEnabled': True, 'rstpEnabled': True, 'stpGuard': 'disabled', 'linkNegotiation': 'Auto negotiate', 'portScheduleId': None, 'udld': 'Alert only', 'accessPolicyType': 'Open'}
    
    accessGuest = {'portId': '1', 'name': 'INTERNET ONLY', 'tags': ['AM:profiled'], 'enabled': True, 'poeEnabled': True, 'type': 'access', 'vlan': 33, 'voiceVlan': None, 'allowedVlans': 'all', 'isolationEnabled': True, 'rstpEnabled': True, 'stpGuard': 'disabled', 'linkNegotiation': 'Auto negotiate', 'portScheduleId': None, 'udld': 'Alert only', 'accessPolicyType': 'Open'}

    VOICEaccess1 = {'portId': '1', 'name': 'Voice Port Type1', 'tags': ['voice', 'AM:profiled'], 'enabled': True, 'poeEnabled': True, 'type': 'access', 'vlan': 6, 'voiceVlan': 555, 'allowedVlans': 'all', 'isolationEnabled': False, 'rstpEnabled': True, 'stpGuard': 'disabled', 'linkNegotiation': 'Auto negotiate', 'portScheduleId': None, 'udld': 'Alert only', 'accessPolicyType': 'Open'}
 
    VOICEaccess2 = {'portId': '1', 'name': 'Voice Port Type2', 'tags': ['voice', 'AM:profiled'], 'enabled': True, 'poeEnabled': True, 'type': 'access', 'vlan': 6, 'voiceVlan': 777, 'allowedVlans': 'all', 'isolationEnabled': False, 'rstpEnabled': True, 'stpGuard': 'disabled', 'linkNegotiation': 'Auto negotiate', 'portScheduleId': None, 'udld': 'Alert only', 'accessPolicyType': 'Open'}

    def log(self,stuff):
        f = open("autoMAC_profile_output.txt","a")
        print(stuff,file=f)
        f.close()

    #portConfig() - configures the profiles in this init
    def __init__(self):
        print(f'{bcolors.OKBLUE}Initializing portConfig')
        timestamp = datetime.isoformat(datetime.now())
        self.log(f'****************************************************************************************')
        self.log(f'Initializing portConfig - {timestamp}')


        #example of CDP 'platform' or LLDP 'systemDescription' Profile, meraki devices use the same values for both fields
        self.ports['Meraki Cloud Managed AP'] = copy.deepcopy(self.APtrunk)
        self.ports['Meraki MR30H Cloud Managed AP'] = copy.deepcopy(self.APtrunk)
       

        #example of a LLDP specific firmware profile, same as below
        #self.ports['Cisco IP Phone CP-DX650, V1, sipdx650.10-2-5-215'] = copy.deepcopy(self.VOICEaccess1)
        
        #example of a CDP Platform profile, same as above more more generic
        #self.ports['Cisco IP Phone DX650'] = copy.deepcopy(self.VOICEaccess1)


        #example of a OUI profile
        self.ports['b0:7d:47'] = copy.deepcopy(self.VOICEaccess2)

        #example of a block for a specific OUI
        self.ports['00:1e:06'] = copy.deepcopy(self.accessBlock)

        #example of a Vendor "manufacturer" profile
        #self.ports['Cisco Systems'] = copy.deepcopy(self.trunkDefault)
        self.ports['Dell'] = copy.deepcopy(self.accessDefault)
        self.ports['Cisco Meraki'] = copy.deepcopy(self.accessGuest)
        self.ports['Meraki'] = copy.deepcopy(self.accessGuest)



        #example of a full MAC profile
        #self.ports['78:2b:cb:9a:c9:37'] = copy.deepcopy(self.accessDefault)

    #client = {'id': 'kf8522b', 'mac': 'b0:7d:47:c1:80:92', 'description': 'SEPB07D47C18092', 'ip': '192.168.128.16', 'ip6': None, 'ip6Local': 'fe80:0:0:0:b27d:47ff:fec1:8092', 'user': None, 'firstSeen': '2020-09-08T18:20:47Z', 'lastSeen': '2020-09-26T21:01:08Z', 'manufacturer': 'Cisco Systems', 'os': None, 'recentDeviceSerial': 'Q2MW-MW3X-LG3U', 'recentDeviceName': 'Core B', 'recentDeviceMac': 'ac:17:c8:f7:8b:00', 'ssid': None, 'vlan': 999, 'switchport': '13', 'usage': {'sent': 3176, 'recv': 24}, 'status': 'Online', 'notes': None, 'smInstalled': False, 'groupPolicy8021x': None}
    
    #MR30h client = {'id': 'k18bda8', 'mac': 'e0:cb:bc:47:42:93', 'description': 'mr30h-e0cbbc474293', 'ip': None, 'ip6': None, 'ip6Local': 'fe80:0:0:0:e2cb:bcff:fe47:4293', 'user': None, 'firstSeen': '2020-09-26T22:53:17Z', 'lastSeen': '2020-09-26T23:03:53Z', 'manufacturer': 'Meraki', 'os': None, 'recentDeviceSerial': 'Q2MW-MW3X-LG3U', 'recentDeviceName': 'Core B', 'recentDeviceMac': 'ac:17:c8:f7:8b:00', 'ssid': None, 'vlan': 999, 'switchport': '19', 'usage': {'sent': 13, 'recv': 0}, 'status': 'Online', 'notes': None, 'smInstalled': False, 'groupPolicy8021x': None}

    #MR30h stats = {'portId': '19', 'enabled': True, 'status': 'Connected', 'errors': [], 'warnings': [], 'speed': '1 Gbps', 'duplex': 'full', 'usageInKb': {'total': 549, 'sent': 435, 'recv': 114}, 'cdp': {'platform': 'Meraki MR30H Cloud Managed AP', 'deviceId': 'e0cbbc474293', 'portId': 'Port 0', 'address': '6.71.66.147', 'version': '1', 'capabilities': 'Router, Switch'}, 'lldp': {'systemName': 'Meraki MR30H - MR30H', 'systemDescription': 'Meraki MR30H Cloud Managed AP', 'portId': '0', 'chassisId': 'e0:cb:bc:47:42:93', 'portDescription': 'eth0', 'systemCapabilities': 'Two-port MAC Relay'}, 'clientCount': 1, 'powerUsageInWh': 0.0, 'trafficInKbps': {'total': 0.0, 'sent': 0.0, 'recv': 0.0}}

    #portStats = [{'portId': '20', 'enabled': True, 'status': 'Connected', 'errors': [], 'warnings': [], 'speed': '1 Gbps', 'duplex': 'full', 'usageInKb': {'total': 171461, 'sent': 129503, 'recv': 41958}, 'cdp': {'platform': 'Meraki Cloud Managed AP', 'deviceId': '683a1efffff9', 'portId': 'Port 0', 'address': '10.0.7.216', 'version': '1', 'capabilities': 'Router, Switch'}, 'lldp': {'systemName': 'Outdoor', 'systemDescription': 'Meraki Cloud Managed AP', 'portId': '0', 'chassisId': '68:3a:1e:ff:ff:f9', 'portDescription': 'eth0', 'systemCapabilities': 'Two-port MAC Relay'}, 'clientCount': 1, 'powerUsageInWh': 146.4, 'trafficInKbps': {'total': 15.9, 'sent': 12.0, 'recv': 3.9}},{'portId': '21', 'enabled': True, 'status': 'Disconnected', 'errors': ['Port disconnected'], 'warnings': [], 'speed': '', 'duplex': '', 'usageInKb': {'total': 0, 'sent': 0, 'recv': 0}, 'clientCount': 0, 'powerUsageInWh': 0.0, 'trafficInKbps': {'total': 0.0, 'sent': 0, 'recv': 0}} ]

    
    def findClient(self, client, portStats):
        DEBUG = False

        #first find CDP/LLDP
        cdpPlatform = ""
        portStat = ""
        portNum = client['switchport']
    
        if DEBUG: print(f'{bcolors.OKBLUE}Looking for Client[{bcolors.OKGREEN}{client}{bcolors.OKBLUE}]')
        for p in portStats:
           if p['portId'] == portNum:
              portStat = p
              if DEBUG: print(f'Found port {p}')

        #Corner case: sometimes find CDP info mirrored on same port on a different switch in stack (port Switch-A-13 has the same info as Switch-B-13) with only chassis identifier as difference
        #if 'lldp' in portStat and portStat['lldp']['chassisId'] == '0.0.0.0':
        #    print(f'\t{bcolors.FAIL}Bogus CDP ghost detected!')
        #    portStat.pop('cdp') #toss CDP as it's worthless
        #    portStat.pop('lldp') #toss LLDP too
 
 
 
        
        #FIRST- Look for a MAC match
        mac = client['mac']
        if mac in self.ports.keys():
            print(f'\t{bcolors.OKBLUE}Detected specific MAC {bcolors.OKGREEN}{bcolors.Bold}{mac}{bcolors.ENDC}')
            return self.ports[mac]
        else:
            print(f'\t{bcolors.OKBLUE}Unknown MAC detected {bcolors.OKGREEN}{bcolors.Bold}{mac}{bcolors.ENDC}')
            if not mac in self.unique:
                self.log(f'New MAC found, [{mac}]')
                self.unique.append(mac)
            #self.log(f'\t{client}')
            #self.log(f'')

        #SECOND - MAC OUI (vendor OUI)
        OUI = client['mac'][:8]
        if OUI in self.ports.keys():
            print(f'\t{bcolors.OKBLUE}Detected Vendor OUI {bcolors.OKGREEN}{bcolors.Bold}{OUI}{bcolors.ENDC}')
            return self.ports[OUI]
        else:
            print(f'\t{bcolors.OKBLUE}Unknown Vendor OUI detected {bcolors.OKGREEN}{bcolors.Bold}{OUI}{bcolors.ENDC}')
            if not OUI in self.unique:
                self.log(f'New OUI found, [{OUI}]')
                self.unique.append(OUI)
            #self.log(f'\t{client}')
            #self.log(f'')

  
        #THIRD - CDP
        if 'cdp' in portStat and 'platform' in portStat['cdp']:
           cdpPlatform = portStat['cdp']['platform']
           if cdpPlatform in self.ports.keys():
              print(f'\t{bcolors.OKBLUE}Detected CDP platform {bcolors.OKGREEN}{bcolors.Bold}{cdpPlatform}{bcolors.ENDC}')
              return self.ports[cdpPlatform]
           else:
              print(f'\t{bcolors.OKBLUE}Unknown CDP platform detected {bcolors.OKGREEN}{bcolors.Bold}{cdpPlatform}{bcolors.ENDC}')
              if not cdpPlatform in self.unique:
                  self.log(f'New CDP found, [{cdpPlatform}]')
                  self.unique.append(cdpPlatform)
              #self.log(f'\t{client}')
              #self.log(f'')


        #FOURTH - LLDP
        if 'lldp' in portStat and 'systemDescription' in portStat['lldp']:
            sd = portStat['lldp']['systemDescription']
            if sd in self.ports.keys():
               print(f'\t{bcolors.OKBLUE}Detected LLDP systemDescription {bcolors.OKGREEN}{bcolors.Bold}{sd}{bcolors.ENDC}')
               return self.ports[sd]
            else:
                print(f'\t{bcolors.OKBLUE}Unknown LLDP systemDescription detected {bcolors.OKGREEN}{bcolors.Bold}{sd}{bcolors.ENDC}')
                if not sd in self.unique:
                    self.log(f'New LLDP found, [{sd}]')
                    self.unique.append(sd)
                #self.log(f'\t{client}')
                #self.log(f'')

      
        #FIFTH - Look for a manufacturer match
        man = client['manufacturer']
        if man in self.ports.keys():
            print(f'\t{bcolors.OKBLUE}Detected Manufacturer {bcolors.OKGREEN}{bcolors.Bold}{man}{bcolors.ENDC}')
            return self.ports[man]
        else:
            print(f'\t{bcolors.OKBLUE}Unknown Manufacturer detected {bcolors.OKGREEN}{bcolors.Bold}{man}{bcolors.ENDC}')
            if not man in self.unique:
                self.log(f'New Manufacturer found, [{man}]')
                self.unique.append(man)
            #self.log(f'\t{client}')
            #self.log(f'')




        print(f'\t\t{bcolors.BLINK_FAIL}No profile found{bcolors.ENDC}{bcolors.OKBLUE}')
        if not client in self.unique:
            self.log(f'No profile found')
            self.log(f'\t{client}')
            self.unique.append(client)
            self.log(f'')



        #Second try MAC OUI
        return     


