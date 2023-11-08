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
