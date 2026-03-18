#!/bin/bash
python3 server.py &
nginx
exec gunicorn public:app -b unix:/tmp/ctf.sock -u ctf -g ctf
