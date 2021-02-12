#!/usr/bin/env python3
import argparse
import csv
import datetime, time
import getpass
import kismet_rest
from kis_track import buildAPIUrl

DEBUG = False
VERBOSE = False
KISMET_HOST = 'localhost'
KISMET_USER = 'kismet'
KISMET_PASS = ''
KISMET_PORT = 2501
KISMET_SSL = False
KISMET_HTTP_PROTOCOL = 'http'
KISMET_HTTPS_PROTOCOL = 'https'
MAC_ADDR = ''
CHECK_INTERVAL = 2
timestr = time.strftime("%Y-%m-%d-%H-%M-%S")

def main():
    global DEBUG, VERBOSE, KISMET_HOST, KISMET_USER, KISMET_PASS, KISMET_PORT, KISMET_SSL, KISMET_HTTP_PROTOCOL, KISMET_HTTPS_PROTOCOL, MAC_ADDR, CHECK_INTERVAL

    try:
        parser = argparse.ArgumentParser(description="Track MAC addresses of interest and log to CSV")
        group1 = parser.add_argument_group("Kismet Server Info")
        group1.add_argument("--host", action="store", dest="host", help="Kismet host name or ip. Default: localhost")
        group1.add_argument("-u", "--user", action="store", dest="username", help="Default: kismet")
        group1.add_argument("-p", "--password", action="store", dest="password", help="Encapsulate password string in single quotes 'examplepassword'")
        group1.add_argument("-s", "--ssl", action="store_true", dest="ssl", help="Use https?")
        group1.add_argument("-P", "--port", action="store", dest="port", help="Default: 2501")
        group1.add_argument("-m", "--mac", action="store", dest="mac_addr", help="Target MAC address", required=True)
        group1.add_argument("-i", action="store", dest="check_interval", type=int, help="Default 2 seconds")
        parser.add_argument("-d", "--debug", action="store_true", dest="debug", help="Enable debugging")
        parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", help="Enable verbose output")
        args = parser.parse_args()

        if args.host:
            KISMET_HOST = args.host
        if args.username:
            KISMET_USER = args.username
        if args.password:
            KISMET_PASS = args.password
        else:
            KISMET_PASS = getpass.getpass("Kismet Password:")
        if args.ssl:
            KISMET_SSL = True
        if args.port:
            KISMET_PORT = args.port
        if args.mac_addr:
            MAC_ADDR = args.mac_addr
        if KISMET_SSL:
            KISMET_HTTP_PROTOCOL = KISMET_HTTPS_PROTOCOL
        if args.check_interval:
            CHECK_INTERVAL = args.check_interval
        if args.debug:
            DEBUG = True
            print(args)
        if args.verbose:
            VERBOSE = True

        api_url = buildAPIUrl(KISMET_HTTP_PROTOCOL, KISMET_HOST, KISMET_PORT, MAC_ADDR, DEBUG, VERBOSE)
        trackMac(api_url)
    except KeyboardInterrupt:
        print(" Exiting...")

def trackMac(api_url):
    last_seen_time = ''
    loop_count = 0
    print(f"Running. Results are being written to {timestr}-track-mac.csv \nctrl+c to exit")
    while True:
        time.sleep(CHECK_INTERVAL)
        devices = kismet_rest.Devices(username=KISMET_USER, password=KISMET_PASS)
        for device in devices.by_mac(fields=['kismet.device.base.last_time', 'kismet.device.base.key', 'kismet.device.base.macaddr', 'kismet.device.base.seenby', 'kismet.device.base.signal'], devices=[MAC_ADDR]):
            last_time = device['kismet.device.base.last_time']
            seenbyuuid = device['kismet.device.base.seenby'][0]['kismet.common.seenby.uuid']
            seenbyrssi = device['kismet.device.base.signal']['kismet.common.signal.last_signal']
            device_data = (device['kismet.device.base.key'], device['kismet.device.base.macaddr'], device['kismet.device.base.last_time'], seenbyrssi, seenbyuuid)
            if last_seen_time == last_time:
                last_seen_time = last_time
            else:
                last_seen_time = last_time
                if VERBOSE:
                    print(device_data)
                with open(f"{timestr}-track-mac.csv", 'a', newline='') as csvfile:
                    dw = csv.writer(csvfile, dialect='excel')
                    if loop_count == 0:
                        if DEBUG:
                            print("headers written")
                        dw.writerow(["device_key", "mac_addr", "last_seen", "signal_rssi", "seenby_uuid"])
                    dw.writerow(device_data)
                    loop_count+=1

if __name__ == "__main__":
    main()
