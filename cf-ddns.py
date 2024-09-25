#!/usr/bin/python

# cf-ddns.py
# by Dave Lambert 2024-09-22
# This is a simple script to get your external/public IP address, and update a CloudFlare DNS record with that IP address via API.

import os
import requests
import json

VERBOSE = True

conf_file = "cf-ddns.conf"

# make these non-global?
api_url = "" # set via loadConf()
api_key = "" # set via loadConf()
zone_id = "" # set via loadConf()
record_id = "" # set via loadConf()
headers = "" # set via loadConf()

def loadConf(filename):
    # load conf file and set the global vars
    global api_url
    global api_key
    global zone_id
    global record_id
    global headers
    vars = json.load(open(filename))

    api_key = vars.get("api_key")
    zone_id = vars.get("zone_id")
    record_id = vars.get("record_id")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    api_url = (
        "https://api.cloudflare.com/client/v4/zones/%(zone_id)s/dns_records/%(record_id)s"
        % {"zone_id": zone_id, "record_id": record_id}
    )

def getIP():
    url = "https://api.ipify.org?format=json"
    #url = "https://api.myip.com"   # another URL to use if the above stops working
    # **maybe eventually make my own at DHN?**
    r = requests.get(url)
    return str(r.json()["ip"])

def compareIP(ip1, ip2):
    return ip1 == ip2

def getRecord():
    r = requests.get(api_url, headers=headers)
    ip = str(r.json()['result']['content'])
    name = str(r.json()['result']['name'])

    return ip,name

def updateRecord(ip):
    # using [https://github.com/creimers/cloudflare-ddns/blob/master/ddns.py] as reference
    data = {"content": ip } # the actual json data we're gonna send
    r = requests.patch(api_url, headers=headers, data=json.dumps(data))
    #if r.status_code != 200:
    #    print(r)

def main():
    loadConf(conf_file)
    ip_actual = getIP()
    ip_dns,name_dns = getRecord()
    if not compareIP(ip_actual,ip_dns):
        if VERBOSE:
            print("\nFQDN: ", name_dns)
            print("\nActual IP: ", ip_actual)
            print("Resolved IP: ", ip_dns)
            print("\nDNS record not in sync.")
            print("\nUpdating DNS record...")
        updateRecord(ip_actual)
        if VERBOSE:
            print("\nDNS record updated.") # add error-handling to this
    else:
        if VERBOSE:
            print("\nFQDN: ", name_dns)
            print("\nActual IP: ", ip_actual)
            print("Resolved IP: ", ip_dns)
            print("\nDNS record is in sync.")
    print()

if __name__ == "__main__":
    main()
