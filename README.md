# TeslaMate to Telegram

Python container that collects data from the Teslamate MQTT and sends messages to a Telegram chatbot.

### Instructions

1. Create a file called `docker-compose.yml` with the following content:
~~~
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
        - CAR_ID=X
        - OPTIONS=state|update_version|display_name
~~~
2. Replace `XXX` with its corresponding values
3. Available options:
- "display_name": Send notification when car name is changed
- "update_version": Send notification when a new version of the car software is available
- "state": Send notification with any change in the status of the car, for example: asleep, charging, ...
4. Start the docker containers with `docker-compose up`. To run the container in the background add the `-d` flag:
~~~
docker-compose up -d
~~~
