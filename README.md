# YoLinkApi

Simple script that will integrate to YoLink IoT devices via MQTT protocol.

## Parts Needed
 - Raspberry Pi (or any Linux enviroment)
 - [YoLink Hub + Door Sensors](https://www.amazon.com/gp/product/B084X9D9HY/ref=ppx_yo_dt_b_asin_title_o04_s00?ie=UTF8&psc=1)
 - [YoLink Garage Door Sensor](https://www.amazon.com/gp/product/B07Z7QQV8K/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)

## Prereqs

[YoLink API Documentation](http://www.yosmart.com/doc/lorahomeapi/#/YLAS/?id=quickstart)

As mentioned in the API documentation wiki, contact Chi Yao (yaochi@yosmart.com)<br/>
to request your YoLink account API keys.

KEEP YOUR YOLINK ACCOUNT API KEYS SECURED!

Ensure you have the following information:
Required YoLink Account API Keys:
 - CSID 
 - CSName
 - CSSecKey
 - SVR_URL

Using a QR Code Scanner, gather all the IoT device(s) serial number (32 char code).<br/>
List them somewhere as they will be required to enable the API for each device.

## YoLink Integration

[YoLink API Documentation](http://www.yosmart.com/doc/lorahomeapi/#/YLAS/?id=quickstart)<br/>
YoLink supports both HTTP callback API (webhook) or MQTT report topic.

This script will go over subscribing to the YoLink MQTT broker topic to receive<br/>
sensor events such as open/close.

Install python required modules:
```bash
/usr/bin/python3 -m pip install -r requirements.txt
```

Add the IoT device(s) serial number to `yolink_data.yml`.

Execute the python script providing your YoLink account API keys:

```bash
* Note: For mqtt_url arg, discard the "https://" in {SVR_URL}

/usr/bin/python3 yolink.py --url {SVR_URL}/openApi \
                           --mqtt_url {SVR_URL} \
                           --mqtt_port 8003 \
                           --csid {CSID} \
                           --csseckey {CSSecKey} \
                           --topic {CSName}/report 
```