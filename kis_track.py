#!/usr/bin/env python3
import re
import signal
import sys

def buildAPIUrl(KISMET_HTTP_PROTOCOL, KISMET_HOST, KISMET_PORT, MAC_ADDR, DEBUG, VERBOSE):
    if validateMac(MAC_ADDR):
        if DEBUG:
            print("%s://%s:%s/devices/by-mac/%s/device.json" % (KISMET_HTTP_PROTOCOL, KISMET_HOST, KISMET_PORT, MAC_ADDR))
        if VERBOSE:
            print("- MAC address validated")
        api_url = ("%s://%s:%s/devices/by-mac/%s/device.json" % (KISMET_HTTP_PROTOCOL, KISMET_HOST, KISMET_PORT, MAC_ADDR))
    else:
        print("Invalid MAC. Make sure you are using : as separators")
        sys.exit()
    return api_url

def validateMac(inputMac):
    if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", inputMac.lower()):
        return 1
