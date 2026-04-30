FROM golang:1.25.0-alpine
WORKDIR /usr/src/app
COPY . .
RUN go build -o /usr/local/bin/app .
CMD ["app"]
