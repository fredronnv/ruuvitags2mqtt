FROM python:3.8

WORKDIR /

RUN apt-get update && apt-get -y install bluez bluez-hcidump

RUN pip install ruuvitag_sensor && pip install paho-mqtt && pip install aioblescan && pip install pyyaml

RUN sed -i -e 's/sudo //' /usr/local/lib/python3.8/site-packages/ruuvitag_sensor/adapters/nix_hci.py && \
    sed -i -e "s/'sudo', '-n', //" /usr/local/lib/python3.8/site-packages/ruuvitag_sensor/adapters/nix_hci.py

COPY ruuvitags_mqtt.py /
COPY entity_key_mappings.yml /
COPY tag_names.yml.example /tag_names.yml

CMD python /ruuvitags_mqtt.py
