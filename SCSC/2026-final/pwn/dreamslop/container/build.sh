#!/bin/bash

docker build -f ./builder.dockerfile -t dreamslop-builder .
docker run --name dreamslop-builder-c dreamslop-builder
docker cp dreamslop-builder-c:/build/dreamslop .
docker container rm dreamslop-builder-c
