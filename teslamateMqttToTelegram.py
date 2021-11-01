import paho.mqtt.client as mqtt
import requests
import sys
import datetime
import calendar
from time import sleep
import os

# TeslaMate config
MQTT_SERVER = os.environ['MQTT_SERVER']
MQTT_PORT = int(os.environ['MQTT_PORT'])

# Tesla car ID, default 1
CAR_ID = os.environ['CAR_ID']

# Telegram config
BOT_TOKEN = os.environ['BOT_TOKEN']
BOT_CHAT_ID = os.environ['BOT_CHAT_ID']

# Select messages for Telegram
OPTIONS = os.environ['OPTIONS'].split("|")

data = { 
  "utc": "",
  "display_name": "",
  "state": "",
  "software_current_version": "",
  "software_new_version": ""
}
botMessage = {
    "send": 1,
    "text": ""
}

def on_connect(client, userdata, flags, rc):
    global botMessage
 
    botMessage = {
        "send": 0,
        "text": "🎉 Ahora estás conectado con _TeslaMate_ 🎉"
    }
    sendToTelegram()

def on_message(client, userdata, message):
    global botMessage
    global data

    channel = ""
    try:
        channel = str(message.topic).split('/')[3]
        payload = str(message.payload.decode("utf-8"))
        text = ""

        match channel:
            case 'display_name':
                if data["display_name"] != "" and data["display_name"] != payload:
                    text = "🚘 ha cambiado su nombre a *{}*".format(payload)
                data["display_name"] = payload
            case 'version':
                data["software_current_version"] = payload
            case 'update_version':
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
            
        if(channel in OPTIONS and botMessage['send'] == 0 and botMessage['text'] != ""):
            sendToTelegram()

        return

    except:
        print("unexpected exception while processing message:", sys.exc_info()[0], message.topic, channel, message.payload)

def sendToTelegram():
    global botMessage

    txt = "*{}* {}"
    txt = txt.format(data["display_name"], botMessage['text'])

    send_text = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage?chat_id=' + BOT_CHAT_ID + '&parse_mode=Markdown&text=' + txt
    response = requests.get(send_text)

    botMessage = {"send": 1, "text": "" }


def main():
    client = mqtt.Client("teslamateToATelegram")
    client.on_connect = on_connect
    client.on_message=on_message

    client.connect(str(MQTT_SERVER), MQTT_PORT)
    client.subscribe("teslamate/cars/"+str(CAR_ID)+"/#")

    client.loop_start()

    while True:
        current_datetime = datetime.datetime.utcnow()
        current_timetuple = current_datetime.utctimetuple()
        data["utc"] = calendar.timegm(current_timetuple)
        
        sleep(5)
    
    client.loop_stop()

if __name__ == '__main__':
    main()