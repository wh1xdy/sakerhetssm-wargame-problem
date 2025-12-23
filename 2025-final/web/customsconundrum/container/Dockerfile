FROM mcr.microsoft.com/playwright/python:v1.57.0-jammy

RUN apt-get update && apt-get install -y supervisor

RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN mkdir /app
COPY /app /app

RUN mkdir /admin
COPY /admin /admin

RUN mkdir /bot
COPY /bot /bot

RUN mkdir /proxy
COPY /proxy /proxy

RUN pip install fastapi naja-atra playwright sqlalchemy passlib python-jose jinja2 marko uvicorn python-multipart aiohttp

ENV ADMIN_API_KEY=332b11898a87f9fd08df8be404882e96
ENV ADMIN_KEY=dd255d7ff25bb1037c6a8a4af3b179e4
ENV SECRET_JWT_KEY=ba27c6cff3ee553cdd5eb4e6eb403d7c
ENV FLAG=SSM{y0ur_fr13nd_5muggl3d_a_b0mb_4nd_ev3ry0ne_expl0d3d_:(}

EXPOSE 8080 8083

CMD ["/usr/bin/supervisord"]