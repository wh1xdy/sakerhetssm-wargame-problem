FROM ubuntu:20.04

RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-pip python3-flask gunicorn nginx

RUN groupadd -g 1337 ctf && useradd -r -u 1337 -g ctf ctf
RUN mkdir -p /home/ctf/templates/ 
RUN mkdir -p /home/ctf/codes/

COPY server.py /home/ctf/
COPY nginx.conf /etc/nginx/nginx.conf
COPY MultiColor.py /home/ctf/
COPY templates/index.html /home/ctf/templates/
COPY requirements.txt /home/ctf/

RUN chown -R root:ctf /home/ctf/
RUN chmod -R 750 /home/ctf/
RUN chmod -R 770 /home/ctf/codes

WORKDIR /home/ctf/

RUN pip install --no-cache-dir -r requirements.txt

CMD nginx && gunicorn server:app -b unix:/tmp/ctf.sock -u ctf -g ctf
