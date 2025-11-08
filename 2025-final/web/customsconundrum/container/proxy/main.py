from naja_atra import route, Request, Response, server
from aiohttp import ClientSession
import os

ADMIN_KEY = os.getenv("ADMIN_KEY", "admin_key")
APP_URL = "http://127.0.0.1:8081"
ADMIN_URL = "http://127.0.0.1:8082"


@route(regexp="/.*")
async def proxy(request: Request = None):
    q = ""
    if request.method == "GET":
        q += "?"
        for k, v in request.parameters.items():
            q += f"{k}={v[0]}&"
        q = q[:-1]

    if "/admin" in request.path:
        has_key = "admin_key" in request.cookies.keys()
        if not has_key:
            return "Missing admin key", 400

        admin_key = request.cookies.get("admin_key").value
        if admin_key == ADMIN_KEY:
            url = ADMIN_URL + request.path.replace("/admin", "") + q
        else:
            url = ADMIN_URL + "/unauthorized"
    else:
        url = APP_URL + request.path + q

    body = request.body
    if not body and request.method == "POST" or request.method == "PUT":
        body = await request.reader.read_to_end()

    async with ClientSession() as session:
        async with session.request(
            method=request.method,
            url=url,
            headers=request.headers,
            data=body,
            timeout=10,
            allow_redirects=False,
        ) as r:
            res = await r.read()
            headers = r.headers
            status = r.status

    return Response(status_code=status, body=res, headers=headers)


if __name__ == "__main__":
    server.start(host="0.0.0.0", port=8080, keep_alive=False)
