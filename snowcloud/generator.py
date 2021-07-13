import uuid
import time
import threading

import requests


class SnowcloudRenewThread(threading.Thread):
    def __init__(self, snowcloud):
        super().__init__()
        self.cloud = snowcloud
        self.stop_event = threading.Event()

    def run(self):
        while not self.stopped():
            self.stop_event.wait(self.cloud.ttl/2)
            if self.stopped():
                continue
            self.cloud.renew()

    def stop(self):
        self.stop_event.set()

    def stopped(self):
        return self.stop_event.isSet()


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
                "user": self.user
            }
        )

        result.raise_for_status()
        result = result.json()

        if result["worker_id"] != self.worker_id:
            raise ValueError("Received invalid renewal from server")

        self.expires_on = result["expires"]
        self.ttl = result["ttl"]

    def generate(self):
        timestamp = int((time.time() - self.EPOCH) * 1000)
        snowflake = (timestamp << 22) | (self.worker_id << 12) | self.increment
        self.increment = (self.increment + 1) & 0xFFF
        return snowflake

    def start_autorenew(self):
        self.thread = SnowcloudRenewThread(self)
        self.thread.start()

    def stop_autorenew(self):
        self.thread.stop()
