#!/bin/bash
set -e

rm -rf ./handout/
mkdir -p ./handout/

cp chall/app.py chall/Dockerfile chall/docker-compose.yml chall/flagout.c chall/mulle.png ./handout/

rm -f ./handout/flag.txt
echo "ctf{example}" > ./handout/flag.txt

cd ./handout/
zip handout.zip mulle.png app.py Dockerfile docker-compose.yml flagout.c flag.txt
rm app.py mulle.png Dockerfile docker-compose.yml flagout.c flag.txt
cd ../

echo "Created handout/handout.zip"