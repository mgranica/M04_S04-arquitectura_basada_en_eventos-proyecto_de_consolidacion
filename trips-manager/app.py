import pymongo
import os
import json
import requests
from kafka import KafkaConsumer

MONGO_CLIENT = os.environ.get("MONGO_CLIENT")
PUBLIC_IP = os.environ.get("PUBLIC_IP")

TOPIC_TRIPS = os.environ.get("TOPIC_DRONES", "cabifly.trips")

client = pymongo.MongoClient(MONGO_CLIENT, tlsAllowInvalidCertificates=True)
db = client.cabifly

consumer = KafkaConsumer(
    TOPIC_TRIPS, bootstrap_servers=[PUBLIC_IP], auto_offset_reset="earliest"
)


for message in consumer:
    try:
        event = json.loads(json.loads(message.value.decode("utf-8"))["payload"])["fullDocument"]
        print(event)
    except json.JSONDecodeError:
        print("Error decoding JSON message.")
        continue

    res = requests.get(
        "http://drones-api:8000/drones",
        params={
            "lon": event["location"][1],
            "lat": event["location"][0],
            "distance": 1000,
        },
    ).json()
    drone = res[0]

    # Example data
    filter_criteria = {"trip_id": event["trip_id"]}
    update_data = {"drone_id": drone["drone_id"], "status": "accepted"}

    db.trips.update_one(filter_criteria, {"$set": update_data})
