
from flask import Flask, render_template, jsonify

import os
import ws_server

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "flaskhals")


@app.route("/")
def index():
    return render_template('index.html')



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
