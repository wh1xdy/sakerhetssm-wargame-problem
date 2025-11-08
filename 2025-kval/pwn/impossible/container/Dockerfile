FROM ubuntu:24.04

RUN apt-get update
RUN apt-get install -y xinetd

RUN groupadd -g 900 ctf && useradd -r -u 900 -g ctf ctf
RUN mkdir -p /home/ctf/

COPY service /home/ctf/
COPY flag.txt /flag
COPY xinetd_config /etc/xinetd.d/

RUN chown -R root:ctf /home/ctf/
RUN chmod -R 750 /home/ctf/

CMD xinetd -dontfork
