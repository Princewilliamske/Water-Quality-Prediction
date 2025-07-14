# monitor.py
from fastapi import APIRouter
import numpy as np
from datetime import datetime
import paho.mqtt.client as mqtt
import json
import threading

router = APIRouter()

# MQTT Config
BROKER = "mqtt.eclipseprojects.io"
TOPIC = "water/iot"

def on_connect(client, userdata, flags, rc):
    print("✅ Connected to MQTT broker")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    print(f"📡 IoT Data Received: {data}")
    # Here you could implement drift checks with incoming data

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

def mqtt_loop():
    client.connect(BROKER)
    client.loop_forever()

threading.Thread(target=mqtt_loop, daemon=True).start()

@router.get("/drift")
def check_drift():
    drift_metric = np.random.random()
    drift_status = "Drift Detected" if drift_metric > 0.8 else "No Drift"
    return {
        "timestamp": datetime.now().isoformat(),
        "drift_metric": drift_metric,
        "status": drift_status
    }
