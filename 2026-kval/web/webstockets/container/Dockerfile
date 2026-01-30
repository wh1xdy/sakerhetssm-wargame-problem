### following is for testing the cron or whatever
FROM debian:bookworm-slim 
ENV DEBIAN_FRONTEND=noninteractive
# Update package list and install jq
RUN apt-get update && \
    apt-get install --no-install-recommends -y jq cron supervisor && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN apt update && apt-get install -y software-properties-common
RUN apt-get install -y python3 python3-pip python3-flask gunicorn nginx curl


COPY nginx.conf /etc/nginx/nginx.conf
COPY fake_data.sh /feeds/fake_data.sh
COPY supervisord.conf /etc/supervisor/
COPY crontab /etc/cron.d/ctf
COPY feeds/*.json /feeds/
COPY entrypoint.sh /entrypoint.sh
COPY secret.txt /secret.txt

RUN groupadd -g 1337 ctf && useradd -r -u 1337 -g ctf ctf
RUN chown -R ctf:ctf /feeds/
RUN chmod +x /feeds/fake_data.sh
RUN mkdir -p /home/ctf/
COPY app/ /home/ctf/app
RUN chown -R ctf:ctf /home/ctf/
RUN chmod -R 750 /home/ctf/

RUN chown -R ctf:ctf /home/ctf/app /feeds && \
    chmod +x /feeds/fake_data.sh /entrypoint.sh && \
    chmod 0644 /etc/cron.d/ctf

RUN pip3 install --no-cache-dir websockets eventlet --break-system-packages



CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
