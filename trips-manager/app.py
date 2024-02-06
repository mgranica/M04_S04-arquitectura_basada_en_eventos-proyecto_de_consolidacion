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
        event = json.loads(message.value.decode("utf-8"))
        print(event)
    except json.JSONDecodeError:
        print("Error decoding JSON message.")
        continue

    trip_id = event["body"]["trip_id"]

    res = requests.get(
        "http://drones-api:8000/drones",
        params={
            "lon": event["body"]["location"][0],
            "lat": event["body"]["location"][1],
            "distance": 1000,
        },
    ).json()
    drone = res[0]

    # Example data
    filter_criteria = {"trip_id": event["body"]["trip_id"]}
    update_data = {"drone_id": drone["drone_id"], "status": "accepted"}

    db.trips.update_one(filter_criteria, {"$set": update_data})
