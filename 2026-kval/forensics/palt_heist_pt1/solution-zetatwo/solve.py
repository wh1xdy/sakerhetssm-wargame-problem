#!/usr/bin/env python3

import json
import base64

# tshark -r ../chall.pcapng -Y 'http.request' -T fields -e http.file_data >! http_data_hex.txt

with open('http_data_hex.txt', 'r') as fin:
    for line in fin:
        line = line.strip()
        if len(line) == 0:
            continue
        line = bytes.fromhex(line)
        
        data = json.loads(line.decode())

        if data['auth']['user'] != 'admin':
            continue

        with open('flag.png', 'wb') as fout:
            fout.write(base64.b64decode(data['image']))
