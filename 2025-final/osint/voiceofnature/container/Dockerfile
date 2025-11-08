FROM debian:bookworm-slim

RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-pip python3-flask gunicorn nginx

RUN groupadd -g 1337 ctf && useradd -r -u 1337 -g ctf ctf
RUN mkdir -p /home/ctf/

COPY server.py /home/ctf/
COPY templates/ /home/ctf/templates/
COPY mrstalkersearch.py /home/ctf/
COPY generateData.py /home/ctf/
COPY secret.py /home/ctf/
COPY killar.csv /home/ctf/
COPY tjejer.csv /home/ctf/
COPY efternamn.csv /home/ctf/
COPY nginx.conf /etc/nginx/nginx.conf

RUN chown -R root:ctf /home/ctf/
RUN chmod -R 750 /home/ctf/

WORKDIR /home/ctf/

CMD nginx && gunicorn server:app -b unix:/tmp/ctf.sock -u ctf -g ctf
