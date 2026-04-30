FROM python:3.12-alpine

RUN pip install requests requestrepo

RUN mkdir -p /app

WORKDIR /app
COPY . /app

ENTRYPOINT ["python", "solve.py"]