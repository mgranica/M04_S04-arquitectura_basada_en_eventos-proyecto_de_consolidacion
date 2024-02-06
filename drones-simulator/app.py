import json
import time
import datetime

import os

from kafka import KafkaProducer
from uuid import uuid4
import numpy as np

PUBLIC_IP = os.environ.get("PUBLIC_IP")

TOPIC_DRONES = os.environ.get("TOPIC_DRONES", "cabifly.drones")

NUM_DRONES = int(os.environ.get("NUM_DRONES", 50))
DISPERSION = float(os.environ.get("DISPERSION", 0.01))
MOVEMENT = float(os.environ.get("MOVEMENT", 0.001))
geo_madrid = (40.4168, -3.7038)

producer = KafkaProducer(
    bootstrap_servers=[PUBLIC_IP],
)


def create_random_drone(center, dispersion):
    return {
        "drone_id": str(uuid4()),
        "location": {
            "type": "Point",
            "coordinates": [
                center[1] + np.random.normal(0, dispersion),
                center[0] + np.random.normal(0, dispersion),
            ],
        },
    }


def update_drone(drone):
    # Only moves at a 50% prob
    if np.random.uniform() > 0.5:
        location = {
            "type": "Point",
            "coordinates": [
                drone["location"]["coordinates"][0] + np.random.normal(0, MOVEMENT),
                drone["location"]["coordinates"][1] + np.random.normal(0, MOVEMENT),
            ],
        }
    else:
        location = drone["location"]

    return {"drone_id": drone["drone_id"], "location": location}


drones = [create_random_drone(geo_madrid, DISPERSION) for _ in range(NUM_DRONES)]

while True:
    drones = [update_drone(d) for d in drones]
    for d in drones:

        message = {
            "event": "drone_update",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "data": d,
        }

        producer.send(
            TOPIC_DRONES, key=d["drone_id"].encode(), value=json.dumps(message).encode()
        )

    time.sleep(max(np.random.normal(2, 0.5), 0))
