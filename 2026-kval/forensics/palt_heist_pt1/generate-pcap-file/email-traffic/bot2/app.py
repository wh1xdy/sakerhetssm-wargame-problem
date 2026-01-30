from flask import Flask, request, jsonify
import smtplib
from email.message import EmailMessage
import textwrap

SMTP_HOST = "smtp"
SMTP_PORT = 1025

USER = "hugh@great-ai-creations"

app = Flask(__name__)

@app.route("/send", methods=["POST"])
def send_mail():
    data = request.get_json()
    
    to_addr = data.get("to", "paltoverflow@paltoverflow.com")
    from_addr = data.get("from", USER)
    subject = data.get("subject", "")
    body = data.get("body", "Default bot message")

    msg = EmailMessage()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = subject

    msg.set_content(body, charset="utf-8", cte="8bit")
    
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.send_message(msg)
        return jsonify({"status": "sent", "to": to_addr}), 200
    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
