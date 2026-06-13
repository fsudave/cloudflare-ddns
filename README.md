# cloudflare-ddns

Keeps a Cloudflare DNS A record in sync with your current public IP. Fetches the IP from [ipify](https://api.ipify.org), compares it to the existing record, and updates via the Cloudflare API only when it has changed.

## Requirements

- Python 3
- `requests` (`dnf install python3-requests` or `pip install requests`)
- A Cloudflare [API token](https://developers.cloudflare.com/fundamentals/api/get-started/create-token/) with DNS edit permission for the zone

## Setup

```bash
git clone git@github.com:fsudave/cloudflare-ddns.git /usr/local/bin/cloudflare-ddns
cd /usr/local/bin/cloudflare-ddns
cp cf-ddns_template.conf cf-ddns.conf
```

Edit `cf-ddns.conf` with your API token, zone ID, and record ID. Zone ID is on the zone **Overview** page in the Cloudflare dashboard (API section, right sidebar); record ID: `curl -s -H "Authorization: Bearer TOKEN" "https://api.cloudflare.com/client/v4/zones/ZONE_ID/dns_records?name=host.example.com" | jq -r '.result[0].id'`

Restrict permissions on the config file:

```bash
chmod 600 cf-ddns.conf
```

Create the log file and test:

```bash
touch cf-ddns.log
./cf-ddns.py
```

## Cron

Run every 15 minutes from root's crontab:

```
*/15 * * * * /usr/local/bin/cloudflare-ddns/cf-ddns.py >/dev/null 2>&1
```

Logs rotate automatically (5 MB, 3 backups) in `cf-ddns.log` alongside the script.
