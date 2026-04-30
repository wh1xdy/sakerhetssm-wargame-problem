#!/bin/bash
rm -rf ./dist
rm -f chall.zip
zip -r chall.zip . -x ".githooks/*" -x bild.png -x challenge.yml -x README.md -x "solution/*" -x "build.sh" -x "chall.zip" -x mariadb/init.sql
mkdir -p dist
mv chall.zip dist/.
