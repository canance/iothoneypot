# IoTHoneypot
##### _A Virtual Machine Introspection Based Multi-Service, Multi-Architecture High-Interaction Honeypot for IoT Devices_

## Usage
Use `docker-compose` to start the containers and then run an interactive `bash` session on the IoTHoneypot container to run the honeypot scripts.
```
$ cd honeypot/docker-compose
$ docker-compose up -d
$ docker exec -it docker-compose_iothoneypot_1 bash
```

## Dependencies
- docker
- docker-compose
