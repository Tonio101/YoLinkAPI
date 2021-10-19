#!/usr/bin/env python3

import argparse
import os
import sys
import yaml

from logger import Logger
from logging import DEBUG
from yolink_devices import YoLinkDeviceApi, YoLinkDoorDevice, YoLinkLeakDevice, \
                           YoLinkTempDevice, DEVICE_TYPE, DeviceType
from yolink_mqtt_client import YoLinkMQTTClient
log = Logger.getInstance().getLogger()


def main(argv):
    usage = ("{FILE} "
             "--config <config_file.yml> "
             "--debug").format(FILE=__file__)
    description = 'Enable Sensor APIs and subscribe to MQTT broker'
    parser = argparse.ArgumentParser(usage=usage, description=description)

    parser.add_argument("-c", "--config", help="Config File",
                        required=True)
    parser.add_argument("-d", "--debug", help="Debug",
                        action='store_true', required=False)

    parser.set_defaults(debug=False)

    args = parser.parse_args()

    if args.debug:
        log.setLevel(DEBUG)

    log.debug("{0}\n".format(args))

    device_hash = {}
    device_serial_numbers = []

    with open(os.path.abspath(args.config), 'r') as fp:
        data = yaml.safe_load(fp)
        device_serial_numbers = data['DEVICE_SERIAL_NUMBERS']

    yolink_api = YoLinkDeviceApi(data['API_URL'], data['CSID'],
                                 data['CSSECKEY'])
    yolink_device = None

    for serial_num in device_serial_numbers:
        yolink_api.build_device_api_request_data(serial_number=serial_num)
        device_data = yolink_api.enable_device_api()

        type = DEVICE_TYPE[device_data['type']]

        if type == DeviceType.DOOR:
            yolink_device = YoLinkDoorDevice(device_data=device_data)
        elif type == DeviceType.TEMPERATURE:
            yolink_device = YoLinkTempDevice(device_data=device_data)
        elif type == DeviceType.LEAK:
            yolink_device = YoLinkLeakDevice(device_data=device_data)
        else:
            raise NotImplementedError

        device_hash[yolink_device.get_id()] = yolink_device

    log.debug(device_hash)

    yolink_client = YoLinkMQTTClient(data['CSID'], data['CSSECKEY'],
                                     data['TOPIC'], data['MQTT_URL'],
                                     data['MQTT_PORT'], device_hash)
    yolink_client.connect_to_broker()


if __name__ == '__main__':
    main(sys.argv)
