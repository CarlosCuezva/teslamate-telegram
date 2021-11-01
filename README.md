# TeslaMate to Telegram

Python container that collects data from the Teslamate MQTT and sends messages to a Telegram chatbot.

### Instructions

1. Create a file called `docker-compose.yml` with the following content:
~~~
docker-compose.yml

version: "3"

services:
  telegrambot:
      image: carlosct/teslamatetotelegram:latest
      restart: always
      environment:
        - MQTT_SERVER=XXX
        - MQTT_PORT=XXX
        - BOT_TOKEN=XXX
        - BOT_CHAT_ID=XXX
~~~
2. Replace `XXX` with its corresponding values
3. Start the docker containers with `docker-compose up`. To run the container in the background add the `-d` flag: