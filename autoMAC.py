#!/usr/bin/python3

### AutoMAC by Nico Darrow


import csv
import meraki
from datetime import datetime
import os, sys
import org_wide_clients
import time
from switchDB import *
from portConfig import *

# TODO
#
# -profiled ports get "excluded" from autoMAC, so once it's profiled it won't auto-configure. 
# -autoProvision - maybe pre-configure ports? wipe_all()


### Tag Logic - 
#  1. Enable API for your ORG
#  2. You need to tag the Network in your ORG with <tag_network_TARGET>
#  3. Tag the switches in that network with <tag_switch_TARGET>
#  4. The script will auto-include orgs/networks/devices that have those tags
#  5. Tag the switch ports with <tag_port_TARGET> and/or <tag_port_AUTO> if you want to allow for port configuration
#  6. The use of <tag_port_AUTO> allows the port to constantly be updated, without it, it'll write once and set the tag to <tag_port_DONE>

### Tag Values - 
tag_network_TARGET = "autoMAC"
tag_switch_TARGET = "autoMAC"
tag_port_TARGET = "AM:on"
tag_port_AUTO = "AM:auto"
tag_port_EXCLUDE = "AM:off"
tag_port_DONE = "AM:complete"

### USER CONFIGURABLE SETTINGS

org_id = '5723437235866696' #this is the org you want to monitor/configure

allowHistoryConfigs = True #this allows it to use historic configs/mac-addresstables
allowProfileConfigs = True #this allows it to "guess" on the profile based on MAC/OUI/CDP/LLDP/Vendor
WRITE  = True #set this to False to test and populate debug log files
reset_switches = False  #setting this to True will default all the ports with any AM tags

### /USER CONFIGURABLE SETTINGS

def client_query():
    print("Querying Clients org-wide for source")
    org_wide_clients.run()
    print("Done Querying Clients")


def cisco_load(msDB, clientDB, sDir):
    print()
    MS = msDB
    loadDirectory(MS, sDir)
    for m in MS:
        for mt in m.macTable:
            if 'port' in mt and not m.isTrunk(mt['port']):
                if not inDB(mt['mac'], clientDB):
                    c = {}
                    c['mac'] = mt['mac']
                    c['vlan'] = mt['vlan']
                    c['port'] = mt['port']
                    if 'name' in mt: c['recentName'] = mt['name']
                    clientDB.append(c)
          #  else:
          #      print(f'MT is a trunk {mt}')
    return




def client_load(clientDB):
    print()
    os.chdir('source')
    files = os.listdir()
    for f in files:
        if f[len(f) - 4:] == ".csv":
            print(f'Opening file {f}')
            with open(f, mode='r') as client_file:
                client_reader = csv.reader(client_file, delimiter=',')
                line_count = 0
                for row in client_reader:
                    if not line_count == 0:
                        C = {}
                        C['netName'] = row[0]
                        C['netId'] = row[1]
                        C['clientId'] = row[2]
                        C['mac'] = row[3]
                        C['desc'] = row[4]
                        C['clientIp'] = row[5]
                        C['clientIp6'] = row[6]
                        C['user'] = row[7]
                        C['firstSeen'] = row[8]
                        C['lastSeen'] = row[9]
                        C['manufacturer'] = row[10]
                        C['os'] = row[11]
                        C['recentSerial'] = row[12]
                        C['recentName'] = row[13]
                        C['recentMac'] = row[14]
                        C['ssid'] = row[15]
                        C['vlan'] = row[16]
                        C['port'] = row[17]
                        C['usage'] = row[18]
                        C['status'] = row[19]
                        clientDB.append(C)

                    line_count += 1
    os.chdir('..')
    return


# checks to see if MAC is in the clientDB source files, if so return the object
def inDB(mac, clientDB):
    result= []
    for c in clientDB:
        if mac == c['mac']:
            return c 
    return None

def validSN(SN, devices):
	if SN == "": return False
	for d in devices:
		if d['serial'] == SN:
			return True
	return False

# the function goes through each switch and assigns priming VLAN and preps it for provisioning
def switch_wipe():
    dashboard = meraki.DashboardAPI(api_key=None, base_url='https://api.meraki.com/api/v1/', print_console=False)
    networks = dashboard.organizations.getOrganizationNetworks(org_id)

    networks_inscope = []  # target networks
    for n in networks:
        if n['tags'] is not None and 'autoMAC' in n['tags']:
            networks_inscope.append(n)


    switches_inscope = []
    devices_inscope = []
    for n in networks_inscope:
        #devices = dashboarad.devices.getNetworkDevices(n['id'])
        devices = dashboard.networks.getNetworkDevices(n['id'])
        
        for d in devices:
            if 'tags' in d and tag_switch_TARGET in d['tags']:
                devices_inscope.append(d)

    for d in devices_inscope:
        serial = d['serial']
        #ports = dashboard.switch_ports.getDeviceSwitchPorts(d['serial'])
        ports = dashboard.switch.getDeviceSwitchPorts(d['serial'])
        for p in ports:
            #if not p['type'] == 'access':
                #print(p)
            #    continue
            #print(p)
            if p['tags'] is None:
                continue
            if "AM:on" in p['tags'] or "AM:auto" in p['tags'] or 'AM:profiled' in p['tags']:
                if tag_port_AUTO in p['tags']:
                    tags = tag_port_TARGET + " " + tag_port_AUTO
                else:
                    tags = tag_port_TARGET
                tags = tags.split(' ')
                port = p['portId']#changed from number
                print(f'{bcolors.FAIL}Reset -> Switch {bcolors.WARNING}{serial}{bcolors.FAIL} Port {bcolors.WARNING}{port}')
                #res2 = dashboard.switch_ports.updateDeviceSwitchPort(serial, port, name='', vlan='999', tags=tags, isolationEnabled=True)
                if(WRITE):
                    res2 = dashboard.switch.updateDeviceSwitchPort(serial, port, name='', vlan='999', type='access', voiceVlan=None, tags=tags, isolationEnabled=False)
                else:
                    print(f'{bcolors.OKGREEN}[READ-ONLY BYPASS]')

    #print(networks_inscope)
    #print(devices_inscope)
    switchCount = len(devices_inscope)
    print(f'{bcolors.OKBLUE}Done.{bcolors.WARNING}  {switchCount}{bcolors.OKBLUE} Switches reset')
    return


# check to see if the port is in scope for configuration
# returns True or False
def isActivePort(serial, port, ports_inscope):
    for p in ports_inscope:
        if not p['serial'] == serial:
            #print(f' {p["serial"]} vs {serial}')
            continue
        if int(p['portId']) == int(port):  #this was broken when i moved to v1, had to make p['portId'] int
            #print("FOUND!")
            return True
        #else:
            #print(f'Did not find port{port} on {serial}{p["portId"]}')

    return False

def log(stuff):
    f = open("autoMAC_output.txt", "a")
    print(stuff,file=f)
    f.close()

def main():

    # this feautre is the "Save_Snapshot" feature
    # client_query() # this queries current org and all client information and builds database
    # exit()

    # clientDB = [{'mac': '00:a6:ca:bd:30:34', 'vlan': '9', 'port': 'Gi1/0/48'},..] List 
    clientDB = []  # this will hold all the client information (port/vlan/etc) from the org_wide_client output
    #client_load(clientDB)  #this loads meraki "snapshot", doesn't include voice vlans, need to fix that

    msDB = []
    sDir = "cisco/paris_raw2/"
    if allowHistoryConfigs:
        cisco_load(msDB, clientDB, sDir)

    #print(clientDB)

    timestamp = datetime.isoformat(datetime.now())
    log(f'Starting autoMAC at {timestamp}')

    if reset_switches: #resets all ports on inscope devies with the tags
        switch_wipe()
        exit()

    # Fire up Meraki API and build DB's
    dashboard = meraki.DashboardAPI(api_key=None, base_url='https://api.meraki.com/api/v1/', log_file_prefix=__file__[:-3], print_console=False)
    loop = True

    #load Port Config detault library
    PC = portConfig()

    networks = dashboard.organizations.getOrganizationNetworks(org_id)
    last_changes = []
    loops_change = 0
    while loop:

        print()
        print(f'{bcolors.HEADER}**************************** START LOOP *****************************')
        print()


        networks_inscope = []  # target networks
        for n in networks:
            if n['tags'] is not None and 'autoMAC' in n['tags']:
                networks_inscope.append(n)
        
        online_devices = []
        stats = dashboard.organizations.getOrganizationDevicesStatuses(org_id)
        for s in stats:
            if s['status'] == 'online' or s['status'] == 'alerting':
                online_devices.append(s['serial'])


        switches_inscope = []
        devices_inscope = []
        for n in networks_inscope:
            #devices = dashboard.devices.getNetworkDevices(n['id'])
            devices = dashboard.networks.getNetworkDevices(n['id'])
            if len(devices) == 0:
                continue
            for d in devices:
                if 'tags' in d and tag_switch_TARGET in d['tags']:
                    #dashboard.devices.blinkNetworkDeviceLeds(n['id'], serial=d['serial'], duration=5, duty=10, period=100 )
                    if d['serial'] in online_devices:
                        dashboard.devices.blinkDeviceLeds(serial=d['serial'], duration=5, duty=10, period=100 )
                        devices_inscope.append(d)

        print(f'{bcolors.OKBLUE}Networks Inscope:')
        for n in networks_inscope:
            name = n['name']
            oid = n['organizationId']
            nid = n['id']
            oname = dashboard.organizations.getOrganization(oid)['name']
            print(f'\t{bcolors.OKBLUE}Network[{bcolors.WARNING}{name}{bcolors.OKBLUE}] Network_ID[{bcolors.WARNING}{nid}{bcolors.OKBLUE}] Org[{bcolors.WARNING}{oname}{bcolors.OKBLUE}] Org_ID[{bcolors.WARNING}{oid}{bcolors.OKBLUE}]')
        print()
        
        print(f'{bcolors.OKBLUE}Devices Inscope:')
        for d in devices_inscope:
            name = d['name']
            model = d['model']
            nid = d['networkId']
            fw = d['firmware']
            print(f'\t{bcolors.OKBLUE}Switch[{bcolors.WARNING}{name}{bcolors.OKBLUE}] Model[{bcolors.WARNING}{model}{bcolors.OKBLUE}] Firmware[{bcolors.WARNING}{fw}{bcolors.OKBLUE}] Network_ID[{bcolors.WARNING}{nid}{bcolors.OKBLUE}]')
        # sets all switches to "primed"
        # switch_wipe(devices_inscope)



        # identify all the ports that we're updating
        ports_inscope = []
        for d in devices_inscope:
            #ports = dashboard.switch_ports.getDeviceSwitchPorts(d['serial'])
            ports = dashboard.switch.getDeviceSwitchPorts(d['serial'])

            serial = d['serial']
            dname = d['name']
            portsIS = 0
            for p in ports:
                if p['tags'] is not None and tag_port_TARGET in p['tags']:
                    newPort = p
                    newPort['serial'] = d['serial']
                    newPort['netId'] = d['networkId']
                    newPort['model'] = d['model']
                    #ports_inscope.append(p)
                    ports_inscope.append(newPort)
                    portsIS += 1
                #else:
                    #exit()
            print()
            print(f'{bcolors.OKBLUE}Checking switch ports:  Switch [{bcolors.WARNING}{dname}{bcolors.OKBLUE}] SN [{bcolors.WARNING}{serial}{bcolors.OKBLUE}] PortsInscope[{bcolors.WARNING}{portsIS}{bcolors.OKBLUE}]')

        #print("Ports Inscope:")
        #print(ports_inscope)

        print()
        #        print("Current Switch Clients:")
        #        print()

        port_changes = []
        total_clients = 0
        # new network device function, works at network level instead of querying each switch
        for n in networks_inscope:
            netid = n['id']
            #clients = dashboard.clients.getNetworkClients(netid, perPage=1000)
            clients = dashboard.networks.getNetworkClients(netid, perPage=1000)
            lastId = ""
            if len(clients) == 1000:
                lastId = clients[999]['id']
                clients = clients + dashboard.networks.getNetworkClients(netid, perPage=1000, startingAfter=lastId)
            lastId = clients[len(clients)-1]['id']
            newclients = dashboard.networks.getNetworkClients(netid, perPage=1000, startingAfter=lastId)
            while len(newclients) >= 1:
                #print(f'Clients {len(clients)}')
                #print(f'NewClients {len(newclients)}')
                #print(lastId)
                clients = clients + newclients
                lastId = newclients[len(newclients)-1]['id']
                newclients = dashboard.networks.getNetworkClients(netid, perPage=1000, startingAfter=lastId)
                if len(newclients) <= 1:
                    break
            
 
            print(f'{bcolors.OKBLUE}Detected total {bcolors.WARNING}{len(clients)}{bcolors.OKBLUE} in Network[{bcolors.WARNING}{n["name"]}{bcolors.OKBLUE}]')
            total_clients = total_clients + len(clients)
            print(f'{bcolors.OKBLUE}TOTAL Clients Detected: {bcolors.WARNING}{len(clients)}{bcolors.OKBLUE} in {bcolors.WARNING}ALL{bcolors.OKBLUE} networks')

            for c in clients: #interate through the ACTIVE clients on dashboard (target switches)
                if c['status'] == "Offline":
                    continue
                update = False
                serial = ""
                serial = c['recentDeviceSerial']
                mac = c['mac']
                vlan = int(c['vlan'])
                port = int(c['switchport']) #yes this is right, coming from API call

                # check to see if the MAC is in the source clientDB, if so, return the object
                sourceClient = inDB(mac, clientDB) 
                if sourceClient is not None: #if there is a response
                #   print(f'Client in db[{sourceClient}] MAC[mac]')
                    if not int(sourceClient['vlan']) == vlan: #if NOT the Dashboard-Clients VLAN matches the configured one....
                        vlan = int(sourceClient['vlan'])
                        update = True
                        ovlan = int(c['vlan'])
                        #print(f'{bcolors.OKGREEN}{c}{bcolors.ENDC}')

                    
                    if isActivePort(serial, port, ports_inscope):
                        
                        print(f'{bcolors.FAIL}VLAN Misconfiguration Client activeVlan[{bcolors.WARNING}{ovlan}{bcolors.FAIL}] OriginalVlan[{bcolors.WARNING}{vlan}{bcolors.FAIL}] Mac[{bcolors.WARNING}{c["mac"]}{bcolors.FAIL}] Manufacturer[{bcolors.WARNING}{c["manufacturer"]}{bcolors.FAIL}] Desc[{bcolors.WARNING}{c["description"]}{bcolors.FAIL}]')
 
                        # if there's a change, make an update
                        if update and c['status'] == "Online": #Changes is to be made and port is up
                            #print(c)
                            print(f'\t{bcolors.OKBLUE}Updating switch[{bcolors.WARNING}{serial}{bcolors.OKBLUE}] client[{bcolors.WARNING}{mac}{bcolors.OKBLUE}] VLAN[{bcolors.WARNING}{vlan}{bcolors.OKBLUE}] PORT[{bcolors.WARNING}{port}{bcolors.OKBLUE}]')
                            log(f'Updating switch[{serial}] client[{mac}] VLAN[{vlan}] PORT[{port}]')

                            print()
                            change = [serial, port, vlan, mac]
                            if not change in last_changes:
                                port_changes.append(change)
                                if WRITE: last_changes.append(change) #only assume it's changing if the script isn't ReadOnly
                            else:
                                print(f'\t-{bcolors.FAIL}Duplicate change detected, bypassing{bcolors.OKGREEN}')
                                loops_change = 0
                            print()
                        elif update:
                            print(f'\t-{bcolors.OKGREEN}Port on switch[{bcolors.WARNING}{serial}{bcolors.OKGREEN}] Port[{bcolors.WARNING}{port}{bcolors.OKGREEN}] should be updated but Status[{bcolors.WARNING}{c["status"]}{bcolors.OKGREEN}]')
                            log(f'Port on switch[{serial}] Port[{port}] should be updated but Status[{c["status"]}]')

                            print()


                else: #if sourceClient is NONE, then it wasn't found, what do we do with unknown clients?
                    #if not c['status']  == 'Online': #make sure it's recent and not something crazy
                    #    print(f'{bcolors.BLINK_FAIL}BARF{bcolors.ENDC}')
                    #    continue
                    switchserial = c['recentDeviceSerial']
                    portnum = c['switchport']
                    if isActivePort(serial, port, ports_inscope) and allowProfileConfigs:            
                        print(f'{bcolors.FAIL}Unknown {bcolors.OKBLUE}client[{bcolors.WARNING}{c["mac"]}{bcolors.OKBLUE}] on Port[{bcolors.WARNING}{port}{bcolors.OKBLUE}] on Serial[{bcolors.WARNING}{serial}{bcolors.OKBLUE}]')
		    	#client = {'id': 'kf8522b', 'mac': 'b0:7d:47:c1:80:92', 'description': 'SEPB07D47C18092', 'ip': '192.168.128.16', 'ip6': None, 'ip6Local': 'fe80:0:0:0:b27d:47ff:fec1:8092', 'user': None, 'firstSeen': '2020-09-08T18:20:47Z', 'lastSeen': '2020-09-26T21:01:08Z', 'manufacturer': 'Cisco Systems', 'os': None, 'recentDeviceSerial': 'Q2MW-MW3X-LG3U', 'recentDeviceName': 'Core B', 'recentDeviceMac': 'ac:17:c8:f7:8b:00', 'ssid': None, 'vlan': 999, 'switchport': '13', 'usage': {'sent': 3176, 'recv': 24}, 'status': 'Online', 'notes': None, 'smInstalled': False, 'groupPolicy8021x': None}
                        #print(f'{bcolors.OKGREEN}{c}')
                        portStats = dashboard.switch.getDeviceSwitchPortsStatuses(c['recentDeviceSerial'])
                        portTMP = PC.findClient(c,portStats)
                        if not portTMP == None:
                            portTMP['portId'] = c['switchport'] 
                            print(f'\t{bcolors.OKBLUE}Received Default port template:{bcolors.WARNING} {portTMP}')
                            if WRITE:
                               portTMP['stpGuard'] = portTMP['stpGuard'].lower()
                               res = dashboard.switch.updateDeviceSwitchPort(c['recentDeviceSerial'], **portTMP)
                               log(f'Profiled port[{portTMP}]')
                               log(f'[WRITE] API updateDeviceSwitchPorts')
                            else:
                               print(f'{bcolors.OKGREEN}[READ-ONLY BYPASS]')
                               log(f'[READ-ONLY] API updateDeviceSwitchPorts')


                        else:
                            print(f'\t{bcolors.FAIL}No default template found.... suggest adding one based on the above values{bcolors.OKBLUE}')

                        print()
                        time.sleep(3)
        
        if not allowProfileConfigs:
            print()
            print(f'{bcolors.OKGREEN} Auto-Profiles are disabled')

        print()
        print(f'{bcolors.OKBLUE}Ports to change: {bcolors.WARNING}{port_changes}{bcolors.OKBLUE}')
        print(f'{bcolors.OKBLUE}Last Changes: {bcolors.WARNING}{last_changes}{bcolors.OKBLUE}')
        print()

        if len(port_changes) == 0:
            print(f'{bcolors.OKGREEN} NO CHANGES')
            loops_change += 1
            if loops_change >= 5: #clear the last change buffer after 5 loops without any modified change
                last_changes = []
                loops_change = 0

        for pc in port_changes:
            S1 = pc[0]
            P1 = pc[1]
            vlan = pc[2]
            mac = pc[3]
            #newPort = dashboard.switch_ports.getDeviceSwitchPort(S1, P1)
            newPort = dashboard.switch.getDeviceSwitchPort(S1,P1)

            if not newPort['type'] == 'access': #short circuit if it's not an access port.
                continue
            
            #Pull original switch port config
            orig_mac = findMAC(msDB,mac)
            orig_sw = getSW(msDB,orig_mac['name'])
            orig_port = orig_sw.parsedCFG(orig_mac['port'])
            oVlan = vlan
            try:
                oVlan = orig_port['vlan']
            except:
                print(f'Failure on port: {orig_port} NewPort[{newPort}]')

            if 'voiceVlan' in orig_port:
                ovoiceVlan = orig_port['voiceVlan']
            else:
                ovoiceVlan = None
            oPort = orig_mac['port']
            oName = orig_mac['name']
            stpG = orig_port['stpGuard']
            print(f'\t{bcolors.OKGREEN}Original port config found: vlan[{bcolors.WARNING}{oVlan}{bcolors.OKGREEN}] voice[{bcolors.WARNING}{ovoiceVlan}{bcolors.OKGREEN}] port[{bcolors.WARNING}{oPort}{bcolors.OKGREEN}] stpGuard[{bcolors.WARNING}{stpG}{bcolors.OKGREEN}] Switch[{bcolors.WARNING}{oName}{bcolors.OKGREEN}]')
            
            if tag_port_AUTO in newPort['tags']:
                tags = tag_port_TARGET + " " + tag_port_AUTO
            else:
                tags = tag_port_DONE
            
            #make tags an array
            tags = tags.split(' ')
            #if the access vlan or voice vlan mismatches, configure the port
            if not str(newPort['vlan']) == oVlan or not str(newPort['voiceVlan']) == ovoiceVlan:
                print(f'\t\t{bcolors.OKGREEN}Changing Switch[{bcolors.WARNING}{S1}{bcolors.OKGREEN}] Port[{bcolors.WARNING}{P1}{bcolors.OKGREEN}] to VLAN[{bcolors.WARNING}{oVlan}{bcolors.OKGREEN}] VoiceVlan[{bcolors.WARNING}{ovoiceVlan}{bcolors.OKGREEN}] stpGuard[{bcolors.WARNING}{stpG}{bcolors.OKGREEN}]')
                log(f'Changing Switch[{S1}] Port[{P1}] to VLAN[{oVlan}] VoiceVlan[{ovoiceVlan}] stpGuard[{stpG}]')

                #res = dashboard.switch_ports.updateDeviceSwitchPort(S1, P1, vlan=oVlan, voiceVlan=ovoiceVlan, tags=tags, isolationEnabled=False, stpGuard=stpG)
                if WRITE:
                    res = dashboard.switch.updateDeviceSwitchPort(S1, P1, vlan=oVlan, voiceVlan=ovoiceVlan, tags=tags, isolationEnabled=False, stpGuard=stpG)
                    log(f'[WRITE] API updateDeviceSwitchPorts')
                else:
                    print(f'{bcolors.OKGREEN}[READ-ONLY BYPASS]')
                    log(f'[READ-ONLY] API updateDeviceSwitchPorts')



            else:
                print(f'{bcolors.FAIL}Port is already configured{bcolors.WARNING}!!!!! Clearing port tag{bcolors.OKBLUE}')
                if WRITE:
                    res = dashboard.switch.updateDeviceSwitchPort(S1, P1, tags=tags)
                    log(f'[WRITE] API updateDeviceSwitchPorts')
                else:
                    print(f'{bcolors.OKGREEN}[READ-ONLY BYPASS]')
                    log(f'[READ-ONLY] API updateDeviceSwitchPorts')


            print()

        print()
        print(f'{bcolors.HEADER}**************************** END LOOP *****************************')
        print()


        time.sleep(15)
        print()
        print()
        # while loop


if __name__ == '__main__':
    main()
