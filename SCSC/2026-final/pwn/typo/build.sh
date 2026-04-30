#!/bin/bash

docker build -f ./builder.dockerfile -t typo-builder .
docker run --name typo-builder-c typo-builder
docker cp typo-builder-c:/build/typo .
docker container rm typo-builder-c
