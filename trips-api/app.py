import pymongo
import os
import datetime
from uuid import uuid4
import json
from kafka import KafkaProducer

from flask import Flask, request, jsonify

MONGO_CLIENT = os.environ.get("MONGO_CLIENT")
PUBLIC_IP = os.environ.get("PUBLIC_IP")

TOPIC_TRIPS = os.environ.get("TOPIC_DRONES", "cabifly.trips")

client = pymongo.MongoClient(MONGO_CLIENT, tlsAllowInvalidCertificates=True)
db = client.cabifly

producer = KafkaProducer(
    bootstrap_servers=[PUBLIC_IP],
)

app = Flask(__name__)


@app.route("/users/<user_id>/trips", methods=["GET"])
def get_trips(user_id):
    trip_list = list(db.trips.find({"user_id": user_id}, {"_id": 0, "user_id": 0}))

    return jsonify({"user_id": user_id, "trips": trip_list})


@app.route("/users/<user_id>/trips", methods=["POST"])
def post_trips(user_id):
    lon = request.json.get("lon")
    lat = request.json.get("lat")

    trip_item = {
        "created_at": datetime.datetime.utcnow().isoformat(),
        "location": [lon, lat],
        "status": "waiting",
        "trip_id": str(uuid4()),
        "user_id": user_id,
    }

    db.trips.insert_one(trip_item)

    trip_item.pop("_id")

    message = {"event": "drone-requested", "body": trip_item}

    producer.send(TOPIC_TRIPS, json.dumps(message).encode("utf-8"))

    return jsonify(trip_item)


# app.run(port=8001)
