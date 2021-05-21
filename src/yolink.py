#!/usr/bin/env python3

import argparse
import os
import sys
import yaml

from logger import getLogger
from yolink_devices import YoLinkDevice
from yolink_mqtt_client import YoLinkMQTTClient
log = getLogger(__name__)

def main(argv):

    usage = ("{FILE} "
            "--url <API_URL> "
            "--csid <ID> "
            "--csseckey <SECKEY> "
            "--mqtt_url <MQTT_URL> "
            "--mqtt_port <MQTT_PORT> "
            "--topic <MQTT_TOPIC>").format(FILE=__file__)

    description = 'Enable Sensor APIs and subscribe to MQTT broker'

    parser = argparse.ArgumentParser(usage=usage, description=description)

    parser.add_argument("-u", "--url",       help="Device API URL",    required=True)
    parser.add_argument("-i", "--csid",      help="Unique Identifier", required=True)
    parser.add_argument("-k", "--csseckey",  help="Security Key",      required=True)
    parser.add_argument("-m", "--mqtt_url",  help="MQTT Server URL",   required=True)
    parser.add_argument("-p", "--mqtt_port", help="MQTT Server Port",  required=True)
    parser.add_argument("-t", "--topic",     help="Broker Topic",      required=True)

    args = parser.parse_args()
    log.debug("{0}\n".format(args))

    device_hash = {}
    device_serial_numbers = []

    with open(os.path.abspath('yolink_data.yml'), 'r') as fp:
        data = yaml.safe_load(fp)
        device_serial_numbers = data['DEVICE_SERIAL_NUMBERS']

    for serial_num in device_serial_numbers:
        yolink_device = YoLinkDevice(args.url, args.csid, args.csseckey, serial_num)
        yolink_device.build_device_api_request_data()
        yolink_device.enable_device_api()

        device_hash[yolink_device.get_id()] = yolink_device

    log.debug(device_hash)

    yolink_client = YoLinkMQTTClient(args.csid, args.csseckey,
            args.topic, args.mqtt_url, args.mqtt_port, device_hash)
    yolink_client.connect_to_broker()

if __name__ == '__main__':
    main(sys.argv)
