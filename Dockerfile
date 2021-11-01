FROM python:3-alpine

WORKDIR /volume1/docker/temp

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "-u", "./teslamateMqttToTelegram.py" ]