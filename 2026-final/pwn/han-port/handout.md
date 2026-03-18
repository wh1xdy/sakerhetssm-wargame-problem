# Svenska Trasselnät
We've made this internal debugging tool to read and debug our electrical grid at different facilities.

This tool allows you to access 5 different electrical grid facilities, each being run at a different place.
You can read the current load at that location, and also send some commands to each grid facility.

## Source Code
Source is provided in `src/`.

- `main.c`: The monitoring terminal — lists connected HAN ports and routes operator commands.
- `ports.c` / `ports.h`: Registry of active grid nodes across the Nordic region, including meter IDs and GPS coordinates.
- `port_proc.c` / `port_proc.h`: Isolation layer — each grid node runs as an independent process to prevent cascading failures.
- `han.c` / `han.h`: Real-time meter simulation engine; produces DSMR P1 telegrams from live grid state.
- `handler.c` / `handler.h`: Firmware command interface exposed by each smart meter node.

Compilation can be done with `gcc -Wall -fno-stack-protector -no-pie -fno-inline -D_FORTIFY_SOURCE=0 -o han-port src/*.c -lm`
