import pymongo
import os
from flask import Flask, request, jsonify
from uuid import uuid4

MONGO_CLIENT = os.environ.get("MONGO_CLIENT")

client = pymongo.MongoClient(MONGO_CLIENT, tlsAllowInvalidCertificates=True)
db = client.cabifly

db.drones.create_index([("location", pymongo.GEOSPHERE)])

app = Flask(__name__)


@app.route("/drones", methods=["GET"])
def get_drones():

    lon = float(request.args.get("lon", -3.7038))
    lat = float(request.args.get("lat", 40.4168))
    distance = int(request.args.get("distance", 50000))

    items = list(
        db.drones.find(
            {
                "location": {
                    "$near": {
                        "$geometry": {"type": "Point", "coordinates": [lon, lat]},
                        "$maxDistance": distance,
                    }
                }
            },
            {"_id": 0},
        )
    )

    return jsonify(items)


# app.run(port=8000)
