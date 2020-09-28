#!/usr/bin/python3

import os
import string
import sys

from ciscoconfparse import CiscoConfParse


class MS_switch:
    name = ""
    vlans = []  # list of vlans
    macs = []  # list of macs in 00:ab:cd:ed:cb:a0  format
    macTable = []  # array of dictionary objects
    unique = 0

    parse = None  # this is the raw CiscoConfParse object
    length = 0

    def __init__(self):
        self.name = ""
        self.macs = []
        self.macTable = []
        self.unique = 0
        self.parse = None
        self.length = 0

    def parseMAC(self):
        print("Parsing MACs")
        parse_MAC = self.parse.find_objects(" DYNAMIC ")
        count = 0
        for pm in parse_MAC:
            pios_tmp = pm.ioscfg[0].split(' ')
            pios = [x for x in pios_tmp if x]  # strips out all the not null
            vlan = pios[0]
            mac = self.baseMAC(pios[1])
            port = pios[3]

            #            print(f'{vlan} {mac} {port}')

            if not mac in self.macs:
                self.macs.append(mac)
            if not vlan in self.vlans:
                self.vlans.append(vlan)
            port = {"mac": mac, "vlan": vlan, "port": port}
            self.macTable.append(port)
            count += 1
        print(f'Loaded {count} macs')
        self.unique = len(self.macTable)
        print(f'Unique = {self.unique}')
        print()
        return

    # this function takes file target and loads it into the parse field
    def parseFile(self, target):
        self.name = target.split(' ')[1].split('.')[0]
        self.parse = CiscoConfParse(target)
        parse_interfaces = self.parse.find_objects('^interface ')
        self.length = str(len(parse_interfaces))
        print(f'Switch {self.name} has {self.length} access ports')
        self.parseMAC()
        return

    # finds the interface associated with port, if theres a "trunk" in the config section, it returns true
    def isTrunk(self, port):
        # "3/0/41" or "Gi3/0/41"
        tmp = port;
        if port[:2] == "Po": #If it's a portchannel, its a trunk
            return True

        if not port[0].isdigit():
            if port[:2] == "Gi":
                tmp = port.split("Gi")[1]
            if port[:2] == "Fa":
                tmp = port.split("Fa")[1]

        if not tmp[0].isdigit():
            print("No Clue what happened")
            sys.exit()

        res = self.parse.find_objects(tmp)[0].ioscfg
        for r in res:
            if "trunk" in r:
                return True
        return False

    def isMAC(self, mac):
        if not len(mac) == 17:
            return False
        macs = mac.split(':')
        if not len(macs) == 6:
            return False

        answer = True
        for m in macs:
            if not len(m) == 2:
                return False
            answer = answer and all(c in string.hexdigits for c in m)

        return answer

    # returns if it's a
    def isCiscoMAC(self, mac):
        if not len(mac) == 14:
            return False
        if mac[4] == '.' and mac[9] == '.':
            # pretty good chance at this point
            mac_split = mac.split('.')
            if not len(mac_split) == 3:
                return False
            mac_first = all(c in string.hexdigits for c in mac_split[0])
            mac_second = all(c in string.hexdigits for c in mac_split[1])
            mac_third = all(c in string.hexdigits for c in mac_split[2])
            return mac_first and mac_second and mac_third  # only true if all three fields
        return False

    # returns regular mac from abcd.1234.abcd to ab:cd:12:34:ab:cd
    def baseMAC(self, ciscoMAC):
        if self.isMAC(ciscoMAC):
            return ciscoMAC

        if not self.isCiscoMAC(ciscoMAC):
            print("Not a Cisco MAC!!!")
            sys.exit()

        newMAC = ['00', '00', '00', '00', '00', '00']
        CM = ciscoMAC.split('.')
        newMAC[0] = CM[0][0:2]
        newMAC[1] = CM[0][2:4]
        newMAC[2] = CM[1][0:2]
        newMAC[3] = CM[1][2:4]
        newMAC[4] = CM[2][0:2]
        newMAC[5] = CM[2][2:4]
        return f'{newMAC[0]}:{newMAC[1]}:{newMAC[2]}:{newMAC[3]}:{newMAC[4]}:{newMAC[5]}'

    # returns True if the MAC exists, otherwise False
    def hasMAC(self, mac):
        if self.isCiscoMAC(mac):
            mac = self.baseMAC(mac)
        if not self.isMAC(mac):
            return False
        if mac in self.macs:
            return True
        else:
            return False

    # returns ports array
    def getMAC(self, mac):
        result = []
        if self.isCiscoMAC(mac):
            mac = self.baseMAC(mac)

        if self.hasMAC(mac):
            for mt in self.macTable:
                if 'mac' in mt and mt['mac'] == mac:
                    result.append(mt)

        return result

    # this returns the config for the port based on MAC address
    def getCFG(self, mac):
        result = []
        if self.isCiscoMAC(mac):
            mac = self.baseMAC(mac)
        mTarget = self.getMAC(mac)
        if len(mTarget) >= 0:
            mTarget = mTarget[0]
        else:
            return result
        
        port = mTarget['port']
        if "Gi" in port:
            port = port.split("Gi")[1] # Gi0/2
        elif "Fa" in port:
            port = port.split("Fa")[1] # Fa0/2
        else:
            print("ERROR, can't parse port type")
            sys.exit()

        configs = self.parse.find_objects("^interface ")
        for c in configs:
            #if port in c.text:
            if c.text.endswith(port):
                result = result + c.ioscfg
                # return c.ioscfg
        #                print(c.ioscfg)
        return result

    ### This returns the port configurations from original config
    # ['interface GigabitEthernet1/0/1', ' description == User Data ==', ' switchport access vlan 73', ' switchport mode access', ' switchport voice vlan 700', ' trust device cisco-phone', ' storm-control broadcast level 95.00', ' storm-control multicast level 95.00', ' storm-control action shutdown', ' storm-control action trap', ' auto qos voip cisco-phone ', ' spanning-tree portfast', ' spanning-tree guard root', ' service-policy input AutoQos-4.0-CiscoPhone-Input-Policy', ' service-policy output AutoQos-4.0-Output-Policy']
    def get_orig_CFG(self, target_port):
        result = []
        port = target_port

        if "Gi" in port:
            port = port.split("Gi")[1] # Gi0/2
        elif "Fa" in port:
            port = port.split("Fa")[1] # Fa0/2
        
        configs = self.parse.find_objects("^interface ")
        for c in configs:
            #if port in c.text:
            if c.text.endswith(port):
                result = result + c.ioscfg
                # return c.ioscfg
        #                print(c.ioscfg)
        return result

    #same as above but returns formatted
    # { 'vlan': <vlan>, 'voiceVlan': <voiceVlan>, "rootGuard": True, "portfast": True, "bpduGuard": false }
    def parsedCFG(self, target_port):
        result = {}
        stpGuard = "disabled"
        oCFG = self.get_orig_CFG(target_port)
        for line in oCFG:
            if "switchport access vlan" in line:
                tmp = line.split(' ')
                vlan = tmp[len(tmp)-1] #grab the last value.   
                result['vlan'] = vlan
            if "switchport voice vlan" in line:
                tmp = line.split(' ')
                voiceVlan = tmp[len(tmp)-1]
                result['voiceVlan'] = voiceVlan
            if "spanning-tree guard root" in line:
                stpGuard = 'root guard'


        result['stpGuard'] = stpGuard

        return result



class bcolors:
 
    ResetAll = "\033[0m"

    Bold       = "\033[1m"
    Dim        = "\033[2m"
    Underlined = "\033[4m"
    Blink      = "\033[5m"
    Reverse    = "\033[7m"
    Hidden     = "\033[8m"

    ResetBold       = "\033[21m"
    ResetDim        = "\033[22m"
    ResetUnderlined = "\033[24m"
    ResetBlink      = "\033[25m"
    ResetReverse    = "\033[27m"
    ResetHidden     = "\033[28m"

    Default      = "\033[39m"
    Black        = "\033[30m"
    Red          = "\033[31m"
    Green        = "\033[32m"
    Yellow       = "\033[33m"
    Blue         = "\033[34m"
    Magenta      = "\033[35m"
    Cyan         = "\033[36m"
    LightGray    = "\033[37m"
    DarkGray     = "\033[90m"
    LightRed     = "\033[91m"
    LightGreen   = "\033[92m"
    LightYellow  = "\033[93m"
    LightBlue    = "\033[94m"
    LightMagenta = "\033[95m"
    LightCyan    = "\033[96m"
    White        = "\033[97m"

    BackgroundDefault      = "\033[49m"
    BackgroundBlack        = "\033[40m"
    BackgroundRed          = "\033[41m"
    BackgroundGreen        = "\033[42m"
    BackgroundYellow       = "\033[43m"
    BackgroundBlue         = "\033[44m"
    BackgroundMagenta      = "\033[45m"
    BackgroundCyan         = "\033[46m"
    BackgroundLightGray    = "\033[47m"
    BackgroundDarkGray     = "\033[100m"
    BackgroundLightRed     = "\033[101m"
    BackgroundLightGreen   = "\033[102m"
    BackgroundLightYellow  = "\033[103m"
    BackgroundLightBlue    = "\033[104m"
    BackgroundLightMagenta = "\033[105m"
    BackgroundLightCyan    = "\033[106m"
    BackgroundWhite        = "\033[107m"

    HEADER = '\033[97m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BLINK_FAIL = Red + Blink

    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
 


###################################################################### NO CLASS ###############################################

# Pass this function the array and directory to parse and it'll fill out the array with switch objects
def loadDirectory(MS, sDir):
    if os.path.isdir(sDir):
        files = os.listdir(sDir)
        for f in files:
            if f[len(f) - 4:] == ".log":
                newSwitch = MS_switch()
                newSwitch.parseFile(sDir + f)
                print(f'Loaded switch {newSwitch.name} with {newSwitch.length} access')
                MS.append(newSwitch)
    print()
    return


# interates through all the switch objects and looks for MAC device and returns that dictionary
# {'mac': '68:23:cb:40:9A:91', 'vlan': '2221', 'port': 'Gi2/0/18', 'name': 'PSDC-W-SW-MDF-St123'}
def findMAC(MS, mac):
    results = []
    if MS == None:
        return None
    for ms in MS:
        tmp = ms.getMAC(mac)
        if tmp == None:
            continue
        else:
            for t in tmp:
                if "port" in t and not 'Po' in t['port']:  # this removes the Port channels
                    t['name'] = ms.name
                    # print(f'{tmp}')
                    if not ms.isTrunk(t['port']):

                        # so here, it should split between voice and non-voice
                        if len(results) == 0:  # first entry, probably wired
                            results.append(t)
                        else:  # second entry, could be voice
                            cf = ms.getCFG(t['mac'])  # returns all lines of IOS cfg, for validation
                            voice = -1
                            for c in cf:  # iterate through the show-run
                                if "voice" in c:  # if there's a CFG line with "voice" in it
                                    bleh = c.split()
                                    for b in bleh:
                                        if b.isdigit():
                                            voice = b  # override the -1

                            if voice == t['vlan']:  # validates the guess matches the switchport
                                # print("BOOYA") #validates that the detected = IOS cfg
                                results[0]['voice'] = t['vlan']  # assign 'ye fawker, bangbang!
                            else:
                                # if the voice vlan doesn't match, then it probably has the voice vlan as the primary VLAN
                                results[0]['voice'] = results[0]['vlan']
                                results[0]['vlan'] = t['vlan']
    if len(results) == 1:
        return results[0]
    return results


# returns switchObject from array
def getSW(MS, switchName):
    for ms in MS:
        if ms.name == switchName:
            return ms

    return


def MAIN_run(argv):
    MS = []

    print("SwitchDB Main")
    if len(argv) == 0:
        print(argv)
        print("ERROR - Please pass it a directory or file")
        sys.exit()

    if os.path.isdir(argv[0]):
        loadDirectory(MS, argv[0])

    elif os.path.isfile(argv[0]):
        newSwitch = MS_switch()
        newSwitch.parseFile(argv[0])
        print(f'Loaded switch {newSwitch.name} with {newSwitch.length} access')
        MS.append(newSwitch)

    else:
        print("Can't parse your arguments.....")
        sys.exit()

    return


if __name__ == "__main__":
    # main(sys.argv[1:])

    MS = []
    sDir = sys.argv[1]
    print(sDir)
    loadDirectory(MS, sDir)
    test = findMAC(MS, '000c.1501.100d')
