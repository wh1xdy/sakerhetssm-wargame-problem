#!/bin/sh
rm handout.zip
zip -r handout.zip container/{templates/,db/,Dockerfile,go*,main.go,queries.sql,schema.sql,sqlc.yaml}
zipinfo handout.zip
