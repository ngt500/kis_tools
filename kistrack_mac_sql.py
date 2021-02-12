#!/usr/bin/env python3
import argparse
import datetime, time
import getpass
import kismet_rest
from kis_track import buildAPIUrl
import pymysql

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
DB_HOST = 'localhost'
DB_USER = ''
DB_PASS = ''
DB_NAME = ''
CHECK_INTERVAL = 2


def main():
    global DEBUG, VERBOSE, KISMET_HOST, KISMET_USER, KISMET_PASS, KISMET_PORT, KISMET_SSL, KISMET_HTTP_PROTOCOL, KISMET_HTTPS_PROTOCOL, MAC_ADDR, DB_HOST, DB_USER, DB_PASS, DB_NAME, CHECK_INTERVAL

    try:
        parser = argparse.ArgumentParser(description="Track MAC addresses of interest and log to MySQL")
        group1 = parser.add_argument_group("Kismet Server Info")
        group1.add_argument("--host", action="store", dest="host", help="Kismet host name or ip. Default: localhost")
        group1.add_argument("-u", "--user", action="store", dest="username", help="Default: kismet")
        group1.add_argument("-p", "--password", action="store", dest="password", help="Encapsulate password string in single quotes 'examplepassword'")
        group1.add_argument("-s", "--ssl", action="store_true", dest="ssl", help="Use https?")
        group1.add_argument("-P", "--port", action="store", dest="port", help="Default: 2501")
        group1.add_argument("-m", "--mac", action="store", dest="mac_addr", help="Target MAC address", required=True)
        group1.add_argument("-i", action="store", dest="check_interval", type=int, help="Default 2 seconds")
        group2 = parser.add_argument_group("MySQL Server Info")
        group2.add_argument("-dbh", "--db_host", action="store", dest="db_host", help="Default: localhost")
        group2.add_argument("-dbu", "--db_user", action="store", dest="db_user", required=True)
        group2.add_argument("-dbp", "--db_pass", action="store", dest="db_pass", help="Encapsulate password string in single quotes 'examplepassword'")
        group2.add_argument("-dbn", "--db_name", action="store", dest="db_name", help="Database name", required=True)
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
        if args.db_host:
            DB_HOST = args.db_host
        if args.db_user:
            DB_USER = args.db_user
        if args.db_pass:
            DB_PASS = args.db_pass
        else:
            DB_PASS = getpass.getpass("DB Password:")
        if args.db_name:
            DB_NAME = args.db_name
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
                print(device["kismet.device.base.key"], device["kismet.device.base.macaddr"], device["kismet.device.base.last_time"], seenbyrssi, seenbyuuid)
                db = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME)
                cursor = db.cursor()
                sql = "INSERT INTO kis_tracked_mac (device_key, mac_addr,last_seen,signal_rssi,seenby_uuid) VALUES ('%s', '%s','%s','%s','%s')" % (device_data)
                try:
                    cursor.execute(sql)
                    db.commit()
                except pymysql.Error as e:
                    print("error pymysql %d: %s" %(e.args[0], e.args[1]))
                    db.rollback()
                    db.close()

if __name__ == "__main__":
    main()
