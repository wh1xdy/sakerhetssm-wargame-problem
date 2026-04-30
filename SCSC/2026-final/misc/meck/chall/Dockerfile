FROM golang:1.26-bookworm

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-pip && \
    pip3 install --break-system-packages flask && \
    rm -rf /var/lib/apt/lists/*

COPY flag.txt /
RUN chmod 400 /flag.txt
COPY flagout.c /
RUN cd /; gcc flagout.c -o flagout && chmod 4111 flagout

RUN useradd --create-home --shell /bin/false compiler

WORKDIR /app
COPY app.py mulle.png ./

EXPOSE 5555
USER compiler
CMD ["python3", "app.py"]
