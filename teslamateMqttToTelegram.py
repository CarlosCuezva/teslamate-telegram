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
    "software_new_version": ""
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
    sendToTelegram()


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

        match topic:
            case 'display_name':
                if data["display_name"] != "" and data["display_name"] != payload:
                    text = "🚘 ha cambiado su nombre a *{}*".format(payload)
                data["display_name"] = payload
            case 'version':
                data["software_current_version"] = payload
            case 'update_version':
                if payload != "" and payload != data["software_current_version"]:
                    data["software_new_version"] = payload
                    text = "🎁  Nueva versión disponible: _{}_".format(payload)
            case 'state':
                if data["state"] != payload:
                    if payload == "online":
                        text = "✨ está despierto"
                    elif payload == "asleep":
                        text = "💤 está dormido"
                    elif payload == "suspended":
                        text = "🛏️ está durmiéndose"
                    elif payload == "charging":
                        text = "🔌 está cargando"
                    elif payload == "offline":
                        text = "🛰️ no está conectado"
                    elif payload == "start":
                        text = "🚀 está arrancando"
                    elif payload == "driving":
                        text = "🏁 está conduciendo"
                    else:
                        text = "⭕ tiene un estado desconocido"

                data["state"] = payload

        if text != "":
            botMessage = {
                "send": 0,
                "text": text
            }

        if topic in OPTIONS and botMessage['send'] == 0 and botMessage['text'] != "":
            sendToTelegram()

        return

    except:
        logger.error("Exception on_message(): ", sys.exc_info()[0], message.topic, message.payload)


def sendToTelegram():
    global botMessage

    txt = "*{}* {}"
    txt = txt.format(data["display_name"], botMessage['text'])

    send_text = 'https://api.telegram.org/bot' + conf.BOT_TOKEN + '/sendMessage?chat_id=' + conf.BOT_CHAT_ID + '&parse_mode=Markdown&text=' + txt
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
