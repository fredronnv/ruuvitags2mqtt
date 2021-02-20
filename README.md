# ruuvitags2mqtt
Simple docker image to export ruuvitags to an mqtt server

## Motivation

RuuviTags are cool little devices that broadcast sensor data over BLE. This script will capture any broadcasted BLE beacons and publish them as MQTT topics to an MQTT broker. Using MQTT relays this can be collected to a central location. The base topic path ```ruuvitags``` is used, modify this by setting RUUVITAG_BASE_TOPIC environment variable.

## Building
build and test using docker-compose
```
$ docker-compose build && docker-compose up
```

## Configuring
The following environment variables are used to control the MQTT server to connect to, MQTT_HOST, MQTT_PORT and MQTT_BIND_ADDRESS.

The environment variable HCI_DEVICE can be used to provide which HCI device do use, default is hci0.

### Human-friendly Topics

By default tags are identified by their MAC address, which is published sans ':' as topics to identify each tag. If you need to customize the topic path with other names an optional file ```tag_names.yml``` can be provided, which will translate the MAC addresses to a readable name. See the provided example.
