from ruuvitag_sensor.ruuvi import RuuviTagSensor
import time
import socket
import sys
import os
import yaml
import json
import paho.mqtt.client as mqtt

device=os.getenv('HCI_DEVICE', default='hci0')

mqttc = mqtt.Client()

mqtt_host = os.getenv('MQTT_HOST', default='127.0.0.1')

debug = os.getenv('DEBUG', default=False)

hass_configured = set()

mqtt_args = dict(
    port=os.getenv('MQTT_PORT', default=1883),
    keepalive=os.getenv('MQTT_KEEPALIVE', default=60),
    #bind_address=os.getenv('MQTT_BIND_ADDRESS', default=mqtt_host)
    )

mqtt_base_topic = os.getenv('RUUVITAG_BASE_TOPIC', default='ruuvitags')
hass_autodiscovery = os.getenv('HASS_AUTODISCOVERY', default=False)
hass_autodiscovery_topic = os.getenv('HASS_AUTODISCOVERY_TOPIC', default='homeassistant')

try:
    mqttc.connect(mqtt_host, **mqtt_args)
except Exception as e:
    print(e)
    print(f"Couldn't connect to {mqtt_host} with {mqtt_args}")
    sys.exit(1)

ruuvitags = {}
entity_key_mappings = {}

try:
    with open('tag_names.yml','r') as f:
        ruuvitags = yaml.safe_load(f)
    with open('entity_key_mappings.yml','r') as f:
        entity_key_mappings = yaml.safe_load(f)
except Exception as e:
    print(e)

def nameify(mac_address):
    if mac_address in ruuvitags.keys():
        return ruuvitags[mac_address]
    else:
        return mac_address.replace(':','')

def hass_autoconfigure(mac_address, name, key):
    object_id = mac_address.replace(':','')
    object_id = f"ruuvitag_{object_id}_{key}"
    entity_id = f"{name.lower()}_{key}"
    msg = {'topic': f'{hass_autodiscovery_topic}/sensor/{object_id}/config'}
    msg['payload'] = {
        'name': f'{name} {key}',
        'object_id': entity_id,
        'unique_id': object_id,
    }
    if key in entity_key_mappings.keys():
        msg['payload'].update(entity_key_mappings[key])
    msg['payload'].update({
        'state_topic': f'{mqtt_base_topic}/{name}/{key}'
    })

    # Convert payload to string
    msg['payload'] = json.dumps(msg['payload'])
    msg['retain'] = True

    return msg

def msgify(mac_address, payload):
    body = []
    t = time.time()
    msgs = []
    name = nameify(mac_address)
    for key in payload.keys():
        unique_key = f"{mac_address}_{key}"
        if key not in ["identifier", "mac"]:
            if hass_autodiscovery and unique_key not in hass_configured:
                try:
                    # If discovery is enable we first unconfigure any previous
                    # configuration to be able to update entity_ids etc...
                    discovery_packet = hass_autoconfigure(mac_address,name,key)
                    msgs.append({'topic': discovery_packet['topic'], 'payload': "", 'retain': False})
                    msgs.append(discovery_packet)
                    hass_configured.add(unique_key)
                except Exception as e:
                    print(f"{e}: when handling hass autoconfigure for {key}")
            try:
                msgs.append({"topic": "%s/%s/%s" % (mqtt_base_topic,name,key), "payload": float(payload[key]), "retain": False})
            except Exception as e:
                print(f"{e}: when handling {key}: {payload[key]}")
    return msgs


def handle_data(found_data):
    key = found_data[0]
    value = found_data[1]
    print(f"Packet from {key}")
    try:
        for m in msgify(key,value):
            mqttc.publish(m['topic'], payload=m['payload'], retain=m['retain'])
    except Exception as e:
        print(f"{e}: {m}")
    sys.stdout.flush()

mqttc.loop_start()
print(f"Started loop with hass autodiscovery {hass_autodiscovery}, base topic {mqtt_base_topic}, autodiscovery topic {hass_autodiscovery_topic}")
try:
    RuuviTagSensor.get_datas(handle_data, bt_device=device)
except Exception as e:
    print(e)
    sys.exit(1)
mqttc.loop_stop()

