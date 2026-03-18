import flask

app = flask.Flask(__name__)
aesthetic_id = None

BASE_URL = "http://127.0.0.1:3333"


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = (
        "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    )
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/")
def solve():
    global aesthetic_id
    if aesthetic_id:
        response = flask.redirect(f"{BASE_URL}/api/aesthetics/{aesthetic_id}")
        aesthetic_id = None
        return response

    return flask.send_file("solve.html")


@app.route("/id", methods=["POST"])
def arm():
    global aesthetic_id
    aesthetic_id = (flask.request.json or {}).get("aestheticId", "").strip()

    response = flask.jsonify({"ok": True})
    return response


@app.route("/back")
def back():
    return flask.make_response(
        "<script>history.back()</script>", 200, {"Content-Type": "text/html"}
    )


@app.route("/leak", methods=["POST"])
def leak():
    print(flask.request.json)
    return flask.jsonify({"status": "success"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
