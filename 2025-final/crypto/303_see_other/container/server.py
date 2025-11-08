from flask import *
from secret import flag
import random
import hashlib

r = random.Random()
salt = r.getrandbits(512)

app = Flask(__name__)

clients = {}


@app.before_request
def before_request():
    user_hash = request.cookies.get("user_hash")
    if user_hash is None:
        user_hash = generate_user_hash(r.getrandbits(128))
    if user_hash not in clients:
        clients[user_hash] = Client(user_hash)
    g.client = clients[user_hash]


@app.after_request
def after_request(response):
    response.set_cookie("user_hash", g.client.hash)
    return response


@app.route("/")
def index():
    return "I was told that the flag is safe from scrapers...", 200


@app.route("/robots.txt")
def robots():
    content = f"User-agent: *\nDisallow: /{g.client.get_flag_path()}"
    return Response(content, mimetype="text/plain")


@app.route("/<path>")
def handle_path(path):
    if path == g.client.get_flag_path():
        return flag, 200
    return f"Path not found", 404


def generate_user_hash(value):
    return hashlib.md5(f"{value}{hex(salt)}".encode()).hexdigest()


class Client:
    def __init__(self, hash):
        self.hash = hash
        self.r = random.Random(generate_user_hash(hash))

    def get_flag_path(self):
        return self.r.getrandbits(128).to_bytes(16, "big").hex()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
