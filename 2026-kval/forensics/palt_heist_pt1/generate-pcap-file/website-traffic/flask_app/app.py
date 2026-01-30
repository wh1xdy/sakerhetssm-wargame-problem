from flask import Flask, request, jsonify, render_template
import smtplib
import random
import jwt
import datetime

# Initialize Flask app
app = Flask(__name__)
SECRET_KEY = "p4lt_4_l1fe_0r_wh4t_d0_y0u_s4y?"

@app.route("/token")
def get_token():
    payload = {
        "user": "temp_user",
        "role": "client",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return jsonify({"token": token})

@app.route('/evaluate', methods=["POST"])
def upload():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON body sent"}), 400

    # Authentication
    auth = data.get("auth")
    if not auth:
        return jsonify({"error": "No auth provided"}), 400

    user = auth.get("user")
    token = auth.get("token")

    # Base64 image
    base64_image = data.get("image")
    if not base64_image:
        return jsonify({"error": "No image provided"}), 400
    
    if user == "admin":
        send_mail()

    # Return score
    return jsonify({
        "success": True,
        "user": user,
        "message": f"Palt recieved score of {random.randint(0,100)}/100" if user == "user" else "Hello Admin, your palt recieved a score of 0/100"
    })

def send_mail():
    s = smtplib.SMTP('smtp', 1025)

    recipe = ""
    with open("./palt_rec.txt", "r", encoding="utf-8") as f:
        recipe = f.read()

    s.sendmail("ai@paltoverflow.com", "kb@REDACTED.com", f"Subject: Forgotten Recipie\r\n\r\n{recipe}")
    s.quit()

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
