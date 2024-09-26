#!/usr/bin/python

# cf-ddns.py
# by Dave Lambert 2024-09-22
# This is a simple script to get your external/public IP address, and update a CloudFlare DNS record with that IP address via API.

import sys
import os
import requests
import json
import logging
logger = logging.getLogger('cf-ddns')

VERBOSE = True

logging.basicConfig(filename='/var/log/cf-ddns.log', level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s: %(message)s')

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
    try:
        logger.debug('Loading config from ' + filename + '...')
        vars = json.load(open(filename))
    except:
        logger.critical('Could not open config file: ' + filename)
        # add better error-handling here
        sys.exit(1)
    logger.debug('Config loaded.')

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
    logger.debug('Obtaining IP from ' + url + '...')
    try:
        r = requests.get(url)
    except:
        logger.critical('Could not obtain IP.')
        # add better error-handling here
        sys.exit(1)
    ip = str(r.json()["ip"])
    logger.debug('Obtained IP ' + ip)
    return ip

def compareIP(ip1, ip2):
    logger.debug('Comparing IPs ' + ip1 + ' vs ' + ip2 + '...')
    if not ip1 == ip2:
        logger.info('IPs do not match.')
    else:
        logger.info('IPs match. Nothing further to do.')
    return ip1 == ip2

def getRecord():
    logger.debug('Obtaining DNS record from ' + api_url + '...')
    try:
        r = requests.get(api_url, headers=headers)
    except:
        logger.critical('Could not obtain DNS record.')
        # add better error-handling here
        sys.exit(1)
    ip = str(r.json()['result']['content'])
    name = str(r.json()['result']['name'])
    logger.debug('Obtained DNS record ' + name + ' which resolves to ' + ip)
    return ip,name

def updateRecord(ip):
    # using [https://github.com/creimers/cloudflare-ddns/blob/master/ddns.py] as reference
    logger.debug('Updating DNS record via API...')
    data = {"content": ip } # the actual json data we're gonna send
    try:
        r = requests.patch(api_url, headers=headers, data=json.dumps(data))
    except:
        logger.critical('Could not update DNS record.')
        # add better error-handling here
        #if r.status_coddde != 200:
        #    print(r)
        sys.exit(1)
    logger.info('DNS record updated.')

def main():
    logger.info('STARTED')
    loadConf(conf_file)
    ip_actual = getIP()
    ip_dns,name_dns = getRecord()
    if not compareIP(ip_actual,ip_dns): updateRecord(ip_actual)
    logger.info('FINISHED') 

if __name__ == "__main__":
    main()
