import threading

from flask import current_app

from snowcloud.generator import Snowcloud

class SnowcloudFlask():
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault("SNOWCLOUD_URL", "")
        app.config.setdefault("SNOWCLOUD_KEY", "")

        app.before_first_request(self.before_first_request)

    def before_first_request(self):
        current_app.snowclouds[threading.get_native_id()] = self.create_client()

    def create_client(self):
        cloud = Snowcloud(
            current_app.config["SNOWCLOUD_URL"],
            current_app.config["SNOWCLOUD_KEY"]
        )

        cloud.register()
        cloud.start_autorenew()

        return cloud

    def generate(self):
        return current_app.snowclouds[threading.get_native_id()].generate()