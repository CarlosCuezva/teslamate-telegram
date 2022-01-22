# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import requests
import sys
from time import sleep
import config as conf
import logging
import logging.handlers

data = {
    "display_name": "",
    "state": "",
    "software_current_version": "",
    "software_new_version": "",
    "battery_level": 100,
    "usable_battery_level": 100,
    "inside_temp": 22,
    "outside_temp": 22,
    "longitude": -5,
    "latitude": 42
}
botMessage = {
    "send": 1,
    "text": ""
}
logger = logging.getLogger()
RESTART = 15
OPTIONS = conf.OPTIONS.split("|")


def setup_logging():
    if conf.DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    handler = logging.handlers.RotatingFileHandler('teslamate2telegram.log', maxBytes=10000000, backupCount=5)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(funcName)s:%(lineno)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def on_connect(client, userdata, flags, rc):
    global botMessage

    if conf.DEBUG:
        logger.info("Connected to the TeslaMate MQTT")

    client.subscribe("teslamate/cars/" + conf.CAR_ID + "/#")

    botMessage = {
        "send": 0,
        "text": "🎉 Ahora estás conectado con _TeslaMate_ 🎉"
    }
    send_to_telegram()


def on_disconnect(client, userdata, rc=0):
    if conf.DEBUG:
        logger.debug("Disconnected: result code " + str(rc))

    client.loop_stop()
    sleep(RESTART)
    create_mqtt_connection()


def on_message(client, userdata, message):
    global botMessage
    global data

    try:
        topic = str(message.topic).split('/')[3]
        payload = str(message.payload.decode("utf-8"))
        text = ""

        if topic == "display_name":
            data["display_name"] = payload
        elif topic == "version":
            data["software_current_version"] = payload
        elif topic == "battery_level":
            data["battery_level"] = payload
        elif topic == "usable_battery_level":
            data["usable_battery_level"] = payload
        elif topic == "inside_temp":
            data["inside_temp"] = payload
        elif topic == "outside_temp":
            data["outside_temp"] = payload
        elif topic == "longitude":
            data["longitude"] = payload
        elif topic == "latitude":
            data["latitude"] = payload
        elif topic == "update_version":
            if payload != "" and payload != data["software_current_version"]:
                data["software_new_version"] = payload
                text = "🎁 Actualización disponible: _{}_".format(payload)
        elif topic == "state":
            if data["state"] != payload:
                if payload == "online":
                    text = "✨ Está despierto"
                elif payload == "asleep":
                    text = "💤 Está dormido"
                elif payload == "suspended":
                    text = "🛏️ Está durmiéndose"
                elif payload == "charging":
                    text = "🔌 Está cargando"
                elif payload == "offline":
                    text = "🛰️ No está conectado"
                elif payload == "start":
                    text = "🚀 Está arrancando"
                elif payload == "driving":
                    text = "🏁 Está conduciendo"
                else:
                    text = "⭕ Estado desconocido"

            data["state"] = payload

        if conf.DEBUG:
            logger.debug(topic + ": " + payload)

        if text != "":
            text = text + "\n🔋{0}% ({1}%)".format(data["usable_battery_level"],data["battery_level"]) \
                  + "\n🌡️ interior {0}ºC".format(data["inside_temp"]) + "\n🌡️ exterior {0}ºC".format(data["outside_temp"]) \
                  + "\n 🌎 [Lat: {0} , Long: {1}](http://maps.google.com/maps?q=loc:{0},{1})".format(data["latitude"], data["longitude"])
            botMessage = {
                "send": 0,
                "text": text
            }

        if topic in OPTIONS and botMessage['send'] == 0 and botMessage['text'] != "":
            send_to_telegram()

    except:
        logger.error("Exception on_message(): ", sys.exc_info()[0], message.topic, message.payload)


def get_formated_text():

    if data["display_name"] != "":
        txt = "*{}* {}".format(data["display_name"], botMessage['text'])
    else:
        txt = "{}".format(botMessage['text'])

    return txt


def send_to_telegram():
    global botMessage

    send_text = 'https://api.telegram.org/bot' + conf.BOT_TOKEN + '/sendMessage?chat_id=' + conf.BOT_CHAT_ID + '&parse_mode=Markdown&disable_web_page_preview=True&text=' + get_formated_text()
    response = requests.get(send_text)
    if conf.DEBUG:
        logger.debug(data)
        logger.debug(response.text)

    botMessage = {"send": 1, "text": ""}


def create_mqtt_connection():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    try:
        if conf.DEBUG:
            logger.info("Trying to connect to the MQTT")

        client.connect(conf.MQTT_SERVER, int(conf.MQTT_PORT), 30)
        client.loop_start()

    except (ValueError, Exception):
        if conf.DEBUG:
            logger.error("Error trying to connect to the MQTT")
        sleep(RESTART)
        create_mqtt_connection()


def main():
    setup_logging()
    create_mqtt_connection()

    while True:
        sleep(5)


if __name__ == '__main__':
    main()
