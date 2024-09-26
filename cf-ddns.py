#!/usr/bin/python

# cf-ddns.py
# by Dave Lambert 2024-09-22
# This is a simple script to get your external/public IP address, and update a CloudFlare DNS record with that IP address via API.

import sys
import os
import requests
import json
import logging

# define some file locations
log_filename = '/var/log/cf-ddns.log'
conf_file = os.path.dirname(os.path.realpath(__file__)) + '/cf-ddns.conf'

# set up logging
logger = logging.getLogger('cf-ddns')
try:
    logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s: %(message)s')
except:
    print('Could not access log file at ' + log_filename + '. Please check that it exists and filesystem permissions.')
    sys.exit(1)

# make these non-global?
api_url = "" # set via loadConf()
api_key = "" # set via loadConf()
zone_id = "" # set via loadConf()
record_id = "" # set via loadConf()
headers = "" # set via loadConf()

def loadConf(filename):
# PURPOSE: load conf file and set the global vars.
    global api_url
    global api_key
    global zone_id
    global record_id
    global headers
    try:
        logger.debug('Loading config from ' + filename + '...')
        config = json.load(open(filename))
    except:
        logger.critical('Could not open config file: ' + filename)
        # add better error-handling here
        sys.exit(1)
    logger.debug('Config loaded.')

    api_key = config.get("api_key")
    zone_id = config.get("zone_id")
    record_id = config.get("record_id")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    api_url = (
        "https://api.cloudflare.com/client/v4/zones/%(zone_id)s/dns_records/%(record_id)s"
        % {"zone_id": zone_id, "record_id": record_id}
    )

def getIP():
# PURPOSE: Gets your IP address via public API.
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
# PURPOSE: Compare two IP addresses (strings) to see if they match.
    logger.debug('Comparing IPs ' + ip1 + ' vs ' + ip2 + '...')
    if not ip1 == ip2:
        logger.info('IPs do not match.')
    else:
        logger.info('IPs match. Nothing further to do.')
    return ip1 == ip2

def getRecord():
# PURPOSE: Obtain DNS record from Cloudflare via API.
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
# PURPOSE: Update the DNS record in Cloudflare via API.
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
