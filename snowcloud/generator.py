import uuid
import time

import requests


class Snowcloud:
    EPOCH = 1577836800

    def __init__(self, url, key):
        self.url = url
        self.key = key
        self.user = str(uuid.uuid4())
        self.increment = 0
        self.thread = None

    def register(self):
        result = requests.post(
            self.url,
            params={
                "key": self.key,
                "user": self.user
            }
        )

        result.raise_for_status()
        result = result.json()

        self.worker_id = result["worker_id"]
        self.expires_on = result["expires"]
        self.ttl = result["ttl"]

    def renew(self):
        result = requests.post(
            self.url,
            params={
                "key": self.key,
                "user": self.user,
                "renew": self.worker_id
            }
        )

        result.raise_for_status()
        result = result.json()

        if result["worker_id"] != self.worker_id:
            raise ValueError("Received invalid renewal from server")

        self.expires_on = result["expires"]
        self.ttl = result["ttl"]

    def check_renew(self):
        if (self.expires_on - time.time() < self.ttl / 2):
            self.renew()

    def generate(self, check_renew=True):
        if check_renew:
            self.check_renew()

        timestamp = int((time.time() - self.EPOCH) * 1000)
        snowflake = (timestamp << 22) | (self.worker_id << 12) | self.increment
        self.increment = (self.increment + 1) & 0xFFF
        return snowflake
