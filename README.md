# README #

### What is this repository for? ###

This is a simple script to get your external/public IP address, and update a CloudFlare DNS record with that IP address via API.

### Dependencies

- Python (developed/tested with Python 3.9.18)
    - [requests](https://pypi.org/project/requests/) module
- Cloudflare API Key for your DNS Zone
    - [https://developers.cloudflare.com/api/](https://developers.cloudflare.com/api/)

### Installation

1. Clone this repo into a suitable location such as `/usr/local/bin`
1. Copy the template file `cf-ddns_template.conf` to `cf-ddns.conf`
    - Edit `cf-ddns.conf` with your API key, Zone ID, and Record ID (obtain from Cloudflare via Postman, for example).
1. Create the log file: `sudo touch /var/log/cf-ddns.log`
1. Test the script by running `./cf-ddns.py`
1. Configure a cronjob to run it at a regular interval, say every 15 mins:
    - Example: `*/15 * * * * /usr/local/bin/cloudflare-ddns/cf-ddns.py >/dev/null 2>&1`
    - Installing it into the `root` user's crontab makes things easy.

