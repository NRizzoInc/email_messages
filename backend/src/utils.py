import os, sys
import json
import getpass
# needed to determine which OS is being used
import re
import platform
import subprocess
# used to get local network exposible IP
import socket
import copy

def loadJson(pathToJson):
    """Wrapper function that makes it easy to load a json"""
    with open(pathToJson, 'r+') as readFile:
        data = json.load(readFile)
    return data

def writeJson(pathToJson, jsonData, indent=4):
    """Wrapper function that makes it easy to write to a json"""
    with open(pathToJson, 'w+') as writeFile:
        json.dump(jsonData, writeFile, indent=indent) #write empty dictionary to file (creates the file)

def keyExists(thisDict, key):
    """Returns true if dictionary contains the key"""
    return key in thisDict

def mergeDicts(dict1, dict2):
    # return {**dict1, **dict2} # doesnt always work
    toRtn = copy.deepcopy(dict1)
    for key in list(dict2.keys()):
        toRtn[key] = dict2[key]
    return toRtn

def isWindows():
    myPlatform = platform.system()
    return myPlatform == "Windows"

def isLinux():
    myPlatform = platform.system()
    return myPlatform == "Linux"

def getIP():
    """Returns your computer's ip address that is accessible by your router"""
    if isWindows():
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        return IPAddr
    elif isLinux():
        ipExpr = r'inet ([^.]+.[^.]+.[^.]+.[^\s]+)'
        output = subprocess.check_output("ifconfig").decode()
        matches = re.findall(ipExpr, output)

        # based on system's setup, might have multiple ip loops running
        # the only one the router actually sees is the one starting with 192.168
        # https://qr.ae/pNs807
        narrowMatches = lambda match: match.startswith("192.168.")
        IPAddr = list(filter(narrowMatches, matches))[0]
        print("Found ip: {0}".format(IPAddr))
        return IPAddr

def keyExists(myDict, key):
    """Returns True or False if 'key' is in 'myDict'"""
    return key in list(myDict.keys())

def containsConfirmation(response):
    """Helper function that returns if 'y' or 'n' is contained within the argument"""
    return 'y' in response or 'n' in response

def promptUntilSuccess(message, successCondition=None, hideInput:bool=False):
    """
        \n@Brief: Keeps prompting user with 'message' until they respond correctly
        \n@Param: message - The message to prompt users with repetitively
        \n@Param: successCondition - (optional) Comparison function that returns a bool -> true means return
        \n@Param: hideInput - (optional) Should 'getpass' be used to hide what the user is typing (i.e. password) 
        \n@Returns: The validated response
    """
    isValidResponse = False
    while isValidResponse == False:
        if hideInput:   response = getpass.getpass(message)
        else:           response = input(message)
        if response != None and len(response) > 0: 
            if successCondition == None:        return response # if no comparison fn, return checked response
            elif successCondition(response):    return response # if returns true, can return valid response
        else: print("Not a valid response")

def isList(objToTest):
    return type(objToTest) is list

def isDict(objToTest):
    return type(objToTest) is dict

def convertToIntList(listToConvert):
    toInt = lambda x: int(x)
    return list(map(toInt, listToConvert))

def convertToStrList(listToConvert):
    toStr  = lambda x: str(x)
    return list(map(toStr, listToConvert))

def isNonEmptyStr(strToTest:str):
    return strToTest != None and len(strToTest) > 0
