# Woodburn Faucet
A simple faucet for Handshake domains

Running on [faucet.woodburn.au](https://faucet.woodburn.au)

## Docker deployment
```
docker run -d \
  --name=faucet \
  -e admin_ip=<your-IP> \
  -e cookie=<your-nb-main-cookie>
  -p 5000:5000 \
  git.woodburn.au/nathanwoodburn/faucet:latest

```

## Optional environment variables
| Variable | Description | Default |
| --- | --- | --- |
| admin_ip | IP address to allow multiple gifts sent to |
| cookie | Cookie to use for nb-main |
| max_price | Maximum price to pay for a domain (in HNS) | 5 |
| max_gifts_per_interval | Maximum number of gifts to send per interval | 24 |
| interval | Interval to send gifts (in seconds) | 86400 (24 hours) |