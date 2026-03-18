FROM debian:bookworm-slim

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y python3 python3-pip python3-flask python3-pil python3-cryptography gunicorn nginx curl fonts-dejavu-core

RUN groupadd -g 1337 ctf && useradd -r -u 1337 -g ctf ctf
RUN mkdir -p /home/ctf/

COPY server.py /home/ctf/
COPY public.py /home/ctf/
COPY templates/ /home/ctf/templates/
COPY static/ /home/ctf/static/
COPY nginx.conf /etc/nginx/nginx.conf

RUN chown -R root:ctf /home/ctf/
RUN chmod -R 750 /home/ctf/
RUN chmod o+x /home/ctf/
RUN chmod -R o+rX /home/ctf/static/

WORKDIR /home/ctf/

COPY start.sh /home/ctf/start.sh
RUN chmod +x /home/ctf/start.sh

CMD ["/home/ctf/start.sh"]
ENV FLAG=SSM{girly_p0p_over_the_fence}

HEALTHCHECK --start-period=20s --start-interval=1s CMD curl -f http://127.0.0.1:1337/ || exit 1
