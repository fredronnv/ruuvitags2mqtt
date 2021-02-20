from ruuvitag_sensor.ruuvi import RuuviTagSensor
import time
import socket
import sys
import os
import yaml
import paho.mqtt.client as mqtt

device=os.getenv('HCI_DEVICE', default='hci0')

mqttc = mqtt.Client()

mqtt_host = os.getenv('MQTT_HOST')

mqtt_args = dict(
    port=os.getenv('MQTT_PORT', default=1883),
    keepalive=os.getenv('MQTT_KEEPALIVE', default=60),
    bind_address=os.getenv('MQTT_BIND_ADDRESS', default="")
    )

mqttc.connect(mqtt_host, **mqtt_args)

ruuvitags = {}

try:
    with open('tag_names.yml','r') as f:
        ruuvitags = yaml.safe_load(f)
except Exception as e:
    print(e)

def msgify(name, payload):
    body = []
    t = time.time()
    msgs = []
    for key in payload.keys():
        if key != "identifier":
            try:
                msgs.append({"topic": "ruuvitags/%s/%s" % (name,key), "payload": float(payload[key])})
            except Exception as e:
                pass
    return msgs

def nameify(mac_address):
    if mac_address in ruuvitags.keys():
        return ruuvitags[mac_address]
    else:
        return mac_address.replace(':','')

def handle_data(found_data):
    key = found_data[0]
    value = found_data[1]
    try:
        for m in msgify(nameify(key),value):
            mqttc.publish(m['topic'], m['payload'])
    except Exception as e:
        print(e)

    sys.stdout.flush()


mqttc.loop_start()
try:
    RuuviTagSensor.get_datas(handle_data, bt_device=device)
except:
    pass
    sys.exit(1)
mqttc.loop_stop()

