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
if os.getenv('CAR_ID') == None:
    CAR_ID = 1
else:
    CAR_ID = os.environ['CAR_ID']

# Telegram config
BOT_TOKEN = os.environ['BOT_TOKEN']
BOT_CHAT_ID = os.environ['BOT_CHAT_ID']

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
        "text": "🎉 Ahora estás conectado con *TeslaMate* 🎉"
    }

def on_message(client, userdata, message):
    global botMessage
    global data

    channel = ""
    try:
        channel = str(message.topic).split('/')[3]
        payload = str(message.payload.decode("utf-8"))

        match channel:
            case 'display_name':
                data["display_name"] = payload
            case 'version':
                data["software_current_version"] = payload
            case 'update_version':
                data["software_new_version"] = payload

                botMessage = {
                    "send": 0,
                    "text": "🎁  Nueva versión disponible: _{}_".format(payload)
                }
            case 'state':
                data["state"] = payload

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

        if(botMessage['send'] == 0 and botMessage['text'] != ""):
            sendToTelegram()
        
        sleep(5)
    
    client.loop_stop()

if __name__ == '__main__':
    main()