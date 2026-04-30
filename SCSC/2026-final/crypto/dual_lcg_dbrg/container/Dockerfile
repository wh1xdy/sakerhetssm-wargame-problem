FROM ubuntu@sha256:186072bba1b2f436cbb91ef2567abca677337cfc786c86e107d25b7072feef0c

RUN apt-get update && apt-get install -y --no-install-recommends \
    socat python3 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/sh ctf

COPY ./flag.py /home/ctf/flag.py
COPY ./dual_lcg_dbrg.py /home/ctf/dual_lcg_dbrg.py
RUN chmod 755 /home/ctf/dual_lcg_dbrg.py

EXPOSE 1337

CMD ["socat", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:/home/ctf/dual_lcg_dbrg.py,su=ctf"]
