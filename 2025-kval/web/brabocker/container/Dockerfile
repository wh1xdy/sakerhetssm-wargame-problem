FROM golang:alpine
RUN apk add sqlite git build-base
RUN mkdir -p /code
WORKDIR /code
COPY . .
ENV CGO_ENABLED=1
RUN go build .
CMD ["./brabocker"]
