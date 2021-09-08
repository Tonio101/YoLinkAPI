from datetime import datetime
import hashlib
import time
import json
import requests
import sys

from enum import Enum
from logger import Logger
log = Logger.getInstance().getLogger()


class DeviceType(Enum):
    DOOR = 1
    TEMPERATURE = 2


class TempType(Enum):
    CELSIUS = 1
    FAHRENHEIT = 2


class DoorEvent(Enum):
    UNKNOWN = -1
    OPEN = 1
    CLOSE = 2


DEVICE_TYPE = {
    "DoorSensor": DeviceType.DOOR,
    "THSensor": DeviceType.TEMPERATURE
}

EVENT_STATE = {
    "normal": DoorEvent.UNKNOWN,
    "open": DoorEvent.OPEN,
    "closed": DoorEvent.CLOSE
}

DEVICE_TYPE_TO_STR = {
    DeviceType.DOOR: "Door Sensor",
    DeviceType.TEMPERATURE: "Temperature Sensor"
}

class YoLinkDeviceApi(object):
    """
    Object representatiaon for YoLink Device API
    """

    def __init__(self, url, csid, csseckey):
        self.url = url
        self.csid = csid
        self.csseckey = csseckey

        self.data = {}
        self.header = {}

    def build_device_api_request_data(self, serial_number):
        """
        Build header + payload to enable sensor API
        """
        self.data["method"] = 'Manage.addYoLinkDevice'
        self.data["time"] = str(int(time.time()))
        self.data["params"] = {'sn': serial_number}

        self.header['Content-type'] = 'application/json'
        self.header['ktt-ys-brand'] = 'yolink'
        self.header['YS-CSID'] = self.csid

        # MD5(data + csseckey)
        self.header['ys-sec'] = \
            str(hashlib.md5((json.dumps(self.data) +
                self.csseckey).encode('utf-8')).hexdigest())

        log.debug("Header:{0} Data:{1}\n".format(self.header, self.data))

    def enable_device_api(self):
        """
        Send request to enable the device API
        """
        response = requests.post(url=self.url,
                                 data=json.dumps(self.data),
                                 headers=self.header)
        log.debug(response.status_code)

        response = json.loads(response.text)
        log.debug(response)

        if response['code'] != '000000':
            log.error("Failed to enable API response!")
            log.info(response)
            sys.exit(2)

        data = response['data']
        log.info("Successfully enabled device API")
        log.info("Name:{0} DeviceId:{1} Type:{2}".format(
            data['name'],
            data['deviceId'],
            data['type']))

        return data


class YoLinkDevice(object):
    """
    Object representatiaon for YoLink Device
    """

    def __init__(self, device_data):
        self.id = device_data['deviceId']
        self.name = device_data['name']
        self.type = DEVICE_TYPE[device_data['type']]
        self.uuid = device_data['deviceUDID']
        self.token = device_data['token']

        # Device data from each MQTT event.
        self.event_payload = {}

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_type(self):
        return self.type

    def get_uuid(self):
        return self.uuid

    def get_token(self):
        return self.token

    def update_device_event_payload(self, data):
        self.event_payload = data

    def get_device_event(self):
        return self.event_payload['event']

    def get_device_event_time(self):
        return datetime.fromtimestamp(
                self.event_payload['time'] / 1000)\
                .strftime("%Y-%m-%d %H:%M:%S")

    def get_current_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_device_message_id(self):
        return self.event_payload['msgid']

    def get_device_data(self):
        return self.event_payload['data']

    def __str__(self):
        to_str = ("Id: {0}\nName: {1}\nType: {2}\nToken: {3}\n"
                  "Event Time: {4}\nCurrent Time: {5}\n").format(
                      self.id,
                      self.name,
                      DEVICE_TYPE_TO_STR[self.type],
                      self.token,
                      self.get_device_event_time(),
                      self.get_current_time()
        )
        return to_str


class YoLinkDoorDevice(YoLinkDevice):
    """
    Object representatiaon for YoLink Door Sensor
    """

    def __init__(self, device_data):
        super().__init__(device_data)

    def isOpen(self):
        return EVENT_STATE[self.get_device_data()['state']] == DoorEvent.OPEN

    def isClose(self):
        return EVENT_STATE[self.get_device_data()['state']] == DoorEvent.CLOSE

    def __str__(self):
        to_str = ("Event: {0} ({1}) \n").format(
            EVENT_STATE[self.get_device_data()['state']],
            self.get_device_data()['state']
        )
        return super().__str__() + to_str


class YoLinkTempDevice(YoLinkDevice):
    """
    Object representatiaon for YoLink Temperature Sensor
    """

    def __init__(self, device_data):
        super().__init__(device_data)
        self.temp = 0.0

    def getTemperature(self, type=TempType.FAHRENHEIT):
        self.temp = float(self.get_device_data()['temperature'])

        if type == TempType.FAHRENHEIT:
            return ((self.temp * 1.8) + 32)

        return self.temp

    def getHumidity(self):
        return float(self.get_device_data()['humidity'])

    def __str__(self):
        to_str = ("Temperature (F): {0}\nHumidity: {1}\n").format(
            self.getTemperature(),
            self.getHumidity()
        )
        return super().__str__() + to_str
