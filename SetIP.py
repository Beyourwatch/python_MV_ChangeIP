from __future__ import print_function
import os
import platform
import sys
# import all the stuff from mvIMPACT Acquire into the current scope
from mvIMPACT import acquire
# import all the mvIMPACT Acquire related helper function such as 'conditionalSetProperty' into the current scope
# If you want to use this module in your code feel free to do so but make sure the 'Common' folder resides in a sub-folder of your project then
from mvIMPACT.Common import exampleHelper

def getNumberFromUser():
    # Since Python 3 'raw_input' became 'input'...
    return int(input())

def getStringFromUser():
    # Since Python 3 'raw_input' became 'input'...
    return str(input())

# Change IP format from HEX to STRING
def convertIP_Hex_To_String(IP_in_HEX):
    block1 = (IP_in_HEX & 0xff000000) >> 24
    block2 = (IP_in_HEX & 0x00ff0000) >> 16
    block3 = (IP_in_HEX & 0x0000ff00) >> 8
    block4 = (IP_in_HEX & 0x000000ff)
    IP_in_STRING = str(block1) + "." + str(block2) + "." + str(block3) + "." + str(block4)

    return IP_in_STRING

def convertIP_STRING_To_HEX(IP_in_STRING):
    block1 = int(IP_in_STRING[0:IP_in_STRING.find(".")])
    IP_in_STRING = IP_in_STRING[IP_in_STRING.find(".") + 1: len(IP_in_STRING)]
    block2 = int(IP_in_STRING[0:IP_in_STRING.find(".")])
    IP_in_STRING = IP_in_STRING[IP_in_STRING.find(".") + 1: len(IP_in_STRING)]
    block3 = int(IP_in_STRING[0:IP_in_STRING.find(".")])
    block4 = int(IP_in_STRING[IP_in_STRING.find(".") + 1: len(IP_in_STRING)])

    IP_in_HEX = (block1 << 24) + (block2 << 16) + (block3 << 8) + block4
    return IP_in_HEX

# open device manager before construct the systemmodule
devMgr = acquire.DeviceManager()

sm = acquire.SystemModule(0)
iInterfaceCount = sm.getInterfaceModuleCount()
print("*********************************************************************************")
print("*This program is used to set the camera IP without GUI")
print("*1. Chose the network card, which is connected to the camera")
print("*2. force camera IP to same subnet")
print("*3. change camera persistent IP")
print("*4. restart camera")
print("*********************************************************************************")
print("find " + str(iInterfaceCount) + " GEV/USB3 interfaces on the pc, please choose one GEV interface to open it!" )
for x in range(0, iInterfaceCount-1):
    sm.interfaceSelector.write(x)
    if sm.interfaceType.readS() == "GEV":
       if sm.interfaceDisplayName.readS() != '':
          print("Index[" + str(x) + "]: " + sm.interfaceDisplayName.readS() + "IP address:" + convertIP_Hex_To_String(sm.gevInterfaceDefaultIPAddress.read()))
       else:
          print("Index[" + str(x) + "]: " + sm.interfaceID.readS() + "IP address:" + convertIP_Hex_To_String(sm.gevInterfaceDefaultIPAddress.read()))

print("Input index and press enter to choose your Interface: " )
selectedInterface = getNumberFromUser()
sm.interfaceSelector.write(selectedInterface)
ifm = acquire.InterfaceModule(sm, selectedInterface)
print("open the interface: " + ifm.interfaceDisplayName.readS()+ " IP:"+ convertIP_Hex_To_String(sm.gevInterfaceDefaultIPAddress.read()))

#select device and show device information
ifm.deviceSelector.write(0)
print("Find Camera: " + ifm.deviceModelName.readS() + " |SN: " + ifm.deviceSerialNumber.readS())
print("Camera IP: " + convertIP_Hex_To_String(ifm.gevDeviceIPAddress.read()))
print("Camera Subnet: " + convertIP_Hex_To_String(ifm.gevDeviceSubnetMask.read()))

#change temporary ip, if camera not in same subnet
print("Do you want to force a temporary IP to Camera? y/n?")
forceIP = getStringFromUser()
if forceIP == "y" or forceIP == "Y":
    print("input your IP:")
    inputIPAddress = getStringFromUser()
    inputIPAddressHex = convertIP_STRING_To_HEX(inputIPAddress)
    print("input your subnet:")
    inputSubnet = getStringFromUser()
    inputSubnetHex = convertIP_STRING_To_HEX(inputSubnet)
    print("input your gateway:")
    inputGateway = getStringFromUser()
    inputGatewayHex = convertIP_STRING_To_HEX(inputGateway)
    print("is setting ip now, please wait")
    ifm.gevDeviceForceIPAddress.write(inputIPAddressHex)
    ifm.gevDeviceForceSubnetMask.write(inputSubnetHex)
    ifm.gevDeviceForceGateway.write(inputGatewayHex)
    ifm.gevDeviceForceIP.call()

else:
    inputIPAddress = ""
    inputSubnet = ""
    inputGateway = ""
    print("NO change IP")

print("*********************************************************************************")
print("please choose a camera to open, then change the persistent IP, update device manager now")
devMgr.updateDeviceList()
deviceCount = devMgr.deviceCount()

for x in range(0, deviceCount):
    chosenDevice = devMgr.getDevice(x)
    chosenDevice.interfaceLayout.writeS("GenICam")
    if chosenDevice.isInUse:
      print("["+str(x)+"]: " + chosenDevice.product.readS() +", "+ chosenDevice.serial.readS() + "Interface: " + chosenDevice.interfaceLayout.readS() + " !!!!Device is IN USE, CANT OPEN!!!")
    else:
      print("[" + str(x) + "]: " + chosenDevice.product.readS() + ", " + chosenDevice.serial.readS() + "Interface: " + chosenDevice.interfaceLayout.readS() + " Device not used, can open")

pDev = devMgr.getDevice(getNumberFromUser())
if pDev == None:
    exampleHelper.requestENTERFromUser()
    sys.exit(-1)
pDev.open()

#need class DeviceControl and TransportLayerControl
mvdc = acquire.DeviceControl(pDev)
mvtlc = acquire.TransportLayerControl(pDev)


mvtlc.gevCurrentIPConfigurationDHCP.write(acquire.bFalse)
mvtlc.gevCurrentIPConfigurationPersistentIP.write(acquire.bTrue)
print("Current IP:      " + convertIP_Hex_To_String(mvtlc.gevCurrentIPAddress.read()) + "   Persistent IP:      " + convertIP_Hex_To_String(mvtlc.gevPersistentIPAddress.read()))
print("Current Subnet:  " + convertIP_Hex_To_String(mvtlc.gevCurrentSubnetMask.read()) + "   Persistent subnet:  " + convertIP_Hex_To_String(mvtlc.gevPersistentSubnetMask.read()))
print("Current Gateway: " + convertIP_Hex_To_String(mvtlc.gevCurrentDefaultGateway.read()) + "   Persistent Gateway: " + convertIP_Hex_To_String(mvtlc.gevPersistentDefaultGateway.read()))
print("*********************************************************************************")
if inputIPAddress == "":
    print("Do you want to change persistent IP? y/n?")
    changePersistentIP = getStringFromUser()
    if changePersistentIP == "y" or changePersistentIP == "Y":
        print("input your IP:")
        inputIPAddress = getStringFromUser()
        inputIPAddressHex = convertIP_STRING_To_HEX(inputIPAddress)
        print("input your subnet:")
        inputSubnet = getStringFromUser()
        inputSubnetHex = convertIP_STRING_To_HEX(inputSubnet)
        print("input your gateway:")
        inputGateway = getStringFromUser()
        inputGatewayHex = convertIP_STRING_To_HEX(inputGateway)
        mvtlc.gevPersistentIPAddress.write(inputIPAddressHex)
        mvtlc.gevPersistentSubnetMask.write(inputSubnetHex)
        mvtlc.gevPersistentDefaultGateway.write(inputGatewayHex)
        print("set ip finished, press any key to restart camera, wait 10 sec to reuse it, will close program")
        input()
        mvdc.deviceReset.call()
    else:
        print("no change IP, will close program")
else:
    print("Do you want to set current IP to persistent IP? y/n?")
    changePersistentIP = getStringFromUser()
    if changePersistentIP == "y" or changePersistentIP == "Y":
        mvtlc.gevPersistentIPAddress.write(inputIPAddressHex)
        mvtlc.gevPersistentSubnetMask.write(inputSubnetHex)
        mvtlc.gevPersistentDefaultGateway.write(inputGatewayHex)
        print("set ip finished, press any key to restart camera, wait 10 sec to reuse it, will close program")
        input()
        mvdc.deviceReset.call()
    else:
        print("no change IP, will close program")

sys.exit(-1)