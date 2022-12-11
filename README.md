# TeslaMate to Telegram

[![](https://img.shields.io/badge/Donate-PayPal-ff69b4.svg)](https://www.paypal.com/donate?hosted_button_id=QF2MBMQZP4V2J)

Script that collects data from the Teslamate via MQTT and sends messages to a Telegram chatbot.

### Requirements

* Python 2.7+
* Install dependencies of Python included in requirements.txt

### Instructions

1. Install all dependencies of Python
~~~
pip install -r requirements.txt
~~~
2. Create the `config.py` file
3. Configure the variables of your MQTT of Teslamate and ABRP inside `config.py` file
~~~
MQTT_SERVER = "@@@@@@@@"                              # MQTT server address (e.g. "127.0.0.1")
MQTT_PORT = "@@@@"                                    # MQTT server port (e.g. "1883")
BOT_TOKEN = "@@@@@@@@@@:@@@@@@@@@@@@@@@@@@@@"         # Bot token
BOT_CHAT_ID = "@@@@@@@@@@"                            # Chat ID
OPTIONS = "update_version"                            # Select options to send notification (options: state, update_version, display_name, (e.g. "state|update_version"))  
CAR_ID = "1"                                          # Car number (usually 1 if you only have a car)
SEND_RESUME = True/False                              # Enable or disable resume when state change to sleep
DEBUG = True/False                                    # Enable or disable debug mode
~~~
4. Run the script
* Run on command line (ideal for testing)
~~~
python ./teslamateMqttToTelegram.py
~~~
* Run in the background
~~~
nohup python ./teslamateMqttToTelegram.py & > /dev/null 2>&1
~~~
## Credits

- Authors: Carlos Cuezva – [List of contributors](https://github.com/carloscuezva/teslamate-telegram/graphs/contributors)
- Distributed under MIT License
