#!/usr/bin/env python3

import requests

BASE_URL = 'http://localhost:50000'

# json: cannot unmarshal object into Go struct field reqS.data of type string
# github.com/hoisie/mustache: line 1: empty tag
# https://github.com/cbroglie/mustache
# https://github.com/cbroglie/mustache/issues/50

data = {
    "template": "{{>/flag.txt}}",
    "data": {
        "recipientName": "",
        "yourName": "",
        "greeting": ""
    }
}
r = requests.post(BASE_URL + '/vykort', json=data)
print(r.status_code)
print(r.text)
