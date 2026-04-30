FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        xinetd \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 ctf

RUN install -d -m 0755 /home/ctf
COPY ./interpreter/dreamslop /home/ctf/dreamslop
COPY run.sh /home/ctf/run.sh
COPY dreamslop.xinetd /etc/xinetd.d/dreamslop
COPY flag.txt /home/ctf/flag.txt

RUN chmod 0755 /home/ctf/dreamslop /home/ctf/run.sh && \
    chmod 0444 /home/ctf/flag.txt && \
    chown -R root:root /home/ctf

EXPOSE 1337

CMD ["/usr/sbin/xinetd", "-dontfork"]
