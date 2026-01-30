FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
      socat ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN id -u ctf >/dev/null 2>&1 || useradd -m ctf
WORKDIR /home/ctf

COPY chall /home/ctf/chall
COPY flag.txt /home/ctf/flag.txt
COPY start.sh /home/ctf/start.sh

RUN chmod 555 /home/ctf/chall /home/ctf/start.sh && chmod 444 /home/ctf/flag.txt

USER ctf
EXPOSE 1337
CMD ["/home/ctf/start.sh"]
