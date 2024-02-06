from kafka import KafkaConsumer
import pymongo
import datetime
import json
import os

MONGO_CLIENT = os.environ.get("MONGO_CLIENT")
PUBLIC_IP = os.environ.get("PUBLIC_IP")

TOPIC_DRONES = os.environ.get("TOPIC_DRONES", "cabifly.drones")

client = pymongo.MongoClient(MONGO_CLIENT, tlsAllowInvalidCertificates=True)
db = client.cabifly

consumer = KafkaConsumer(
    TOPIC_DRONES, bootstrap_servers=[PUBLIC_IP], auto_offset_reset="earliest"
)

for message in consumer:
    try:
        message_data = json.loads(message.value.decode("utf-8"))["data"]
        # print(message_data)
    except json.JSONDecodeError:
        print("Error decoding JSON message.")
        continue

    # Example data
    filter_criteria = {"drone_id": message_data["drone_id"]}
    update_data = {"location": message_data["location"]}

    # Update or insert the document with upsert
    db.drones.update_one(
        filter_criteria,
        {
            # "$set": message_data,
            "$setOnInsert": update_data
        },
        upsert=True,
    )
