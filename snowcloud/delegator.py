import os
import time

import redis
from flask import Flask, request, jsonify


app = Flask(__name__)
db = redis.from_url(os.environ["REDIS_URL"], decode_responses=True)

TIME_TO_LIVE = 60

if not db.exists("snowcloud:id:pool"):
    for i in range(2**10):
        db.zadd("snowcloud:id:pool", {i: 0})


@app.post("/")
def index():
    user = request.args["user"]
    key = request.args["key"]
    renew = request.args.get("renew")

    if not db.sismember("snowcloud:keys", key):
        return "Invalid key", 403

    if renew:
        expires_on = db.zscore("snowcloud:id:pool", renew)
        if not expires_on:
            return "Invalid Worker ID", 400

        registered_by = db.get(f"snowcloud:id:user:{renew}")
        if registered_by != user:
            return "ID not registered by this user", 403

        worker_id = renew
    else:
        worker_id = db.zrange("snowcloud:id:pool", 0, 0)[0]

        expires_on = db.zscore("snowcloud:id:pool", worker_id)

        if float(expires_on) > time.time():
            return "No IDs available", 500

        db.set(f"snowcloud:id:user:{worker_id}", user)

    expires_on += TIME_TO_LIVE
    db.zadd("snowcloud:id:pool", {worker_id: expires_on})

    return jsonify(
        worker_id=int(worker_id),
        expires=float(expires_on),
        ttl=TIME_TO_LIVE
    )

if __name__ == "__main__":
    app.run()