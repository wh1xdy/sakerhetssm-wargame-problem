FROM golang:1.22-alpine AS build

COPY . /build

WORKDIR /build

RUN go build -o /server main.go 

FROM scratch

COPY --from=build /server /server
COPY flag.txt /flag.txt

ENTRYPOINT ["/server"]