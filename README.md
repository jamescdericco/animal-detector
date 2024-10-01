# Run Server
```sh
source setup.env
flask --app server run --no-debug -h 192.168.1.32 -p 5000 --cert ssl/server.crt --key ssl/server.key
```
