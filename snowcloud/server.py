import os

from flask import Flask

from snowcloud.flask_ext import SnowcloudFlask

app = Flask(__name__)
cloud = SnowcloudFlask(app)


app.config["SNOWCLOUD_URL"] = os.environ["SNOWCLOUD_URL"]
app.config["SNOWCLOUD_KEY"] = os.environ["SNOWCLOUD_KEY"]


@app.get("/")
def index():
    return str(cloud.generate())

if __name__ == "__main__":
    app.run()