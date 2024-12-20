import json
import random
import string
import sys
import time
from datetime import datetime

import paho.mqtt.client as mqtt
import requests

from config import API_KEY


def get_weather_data(lat, lon, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    if 'main' in data:
        return data['main']['temp'], data['main']['humidity'], data['main']['pressure']
    else:
        print("Error: 'main' key not found in the API response")
        print("Response:", data)
        return None, None, None


def generate_node_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))


def main(lat, lon, period, mqtt_server, mqtt_topic, api_key):
    node_id = generate_node_id()
    client = mqtt.Client()
    client.connect(mqtt_server)

    try:
        while True:
            try:
                temp, humidity, pressure = get_weather_data(lat, lon, api_key)
                timestamp = datetime.now().isoformat()
                message = {
                    "node_id": node_id,
                    "timestamp": timestamp,
                    "temperature": temp,
                    "pressure": pressure,
                    "humidity": humidity
                }
                client.publish(mqtt_topic, json.dumps(message))
                print(f"Published: {message}")
            except KeyError as e:
                print(f"Error fetching weather data: {e}")
            time.sleep(period)
    except KeyboardInterrupt:
        print("Program terminated by user")


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python laboratory3_pub.py <lat> <lon> <period> <mqtt_server> <mqtt_topic>")
        sys.exit(1)
    lat = sys.argv[1]
    lon = sys.argv[2]
    period = int(sys.argv[3])
    mqtt_server = sys.argv[4]
    mqtt_topic = sys.argv[5]
    api_key = API_KEY
    main(lat, lon, period, mqtt_server, mqtt_topic, api_key)
