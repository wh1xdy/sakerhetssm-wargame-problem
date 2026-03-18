import base64
import urllib.request

from flask import Flask, render_template, request

app = Flask(__name__)

MAX_RANGE = 50


@app.route("/")
def index():
    return render_template("public.html")


@app.route("/track", methods=["POST"])
def track():
    url = request.form.get("url", "").strip()
    if not url:
        return render_template("track.html", error="Please enter a URL.")

    try:
        start = int(request.form.get("start", 0))
        end = int(request.form.get("end", MAX_RANGE))
    except ValueError:
        return render_template("track.html", error="Invalid byte range.")

    if start < 0 or end < start:
        return render_template("track.html", error="Invalid byte range.")

    if end - start > MAX_RANGE:
        return render_template(
            "track.html",
            error=f"Max {MAX_RANGE} bytes per request (requested {end - start}).",
        )

    try:
        resp = urllib.request.urlopen(url, timeout=5)
        body = resp.read()
    except Exception as e:
        return render_template("track.html", error=str(e))

    chunk = body[start:end]
    encoded = base64.b64encode(chunk.hex().encode()).decode()

    return render_template(
        "track.html",
        url=url,
        start=start,
        end=min(end, len(body)),
        total=len(body),
        encoded=encoded,
    )
