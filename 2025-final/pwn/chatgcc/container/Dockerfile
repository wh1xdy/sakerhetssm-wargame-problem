# Setting up chroot below
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y build-essential xinetd
RUN groupadd -g 1337 ctf && useradd -r -u 1337 -g ctf ctf
RUN mkdir -p /home/ctf/

COPY service /home/ctf/
COPY flag.txt /
COPY xinetd.conf /etc/

RUN chown -R root:root /home/ctf/
RUN chmod 755 /flag.txt
RUN chmod -R 755 /home/ctf/

CMD ["/usr/sbin/xinetd", "-dontfork", "-f", "/etc/xinetd.conf"]