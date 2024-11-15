import paho.mqtt.client as mqtt
import json
import sys
from bottle import route, run, template
import matplotlib.pyplot as plt
import io
import base64

messages = []

def on_message(client, userdata, msg):
    global messages
    data = json.loads(msg.payload)
    messages.append(data)
    if len(messages) > n:
        messages.pop(0)

@route('/')
def index():
    global messages
    temps = [msg['temperature'] for msg in messages]
    hums = [msg['humidity'] for msg in messages]
    press = [msg['pressure'] for msg in messages]
    timestamps = [msg['timestamp'] for msg in messages]

    fig, ax = plt.subplots(3, 1, figsize=(10, 8))
    ax[0].plot(timestamps, temps, label='Temperature')
    ax[1].plot(timestamps, hums, label='Humidity')
    ax[2].plot(timestamps, press, label='Pressure')

    for a in ax:
        a.legend()
        a.set_xticklabels(timestamps, rotation=45, ha='right')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return template('<img src="data:image/png;base64,{{img}}" />', img=img)

def main(mqtt_server, mqtt_topic, n):
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(mqtt_server)
    client.subscribe(mqtt_topic)
    client.loop_start()
    run(host='localhost', port=8080)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python laboratory3_sub.py <mqtt_server> <mqtt_topic> <n>")
        sys.exit(1)
    mqtt_server = sys.argv[1]
    mqtt_topic = sys.argv[2]
    n = int(sys.argv[3])
    main(mqtt_server, mqtt_topic, n)