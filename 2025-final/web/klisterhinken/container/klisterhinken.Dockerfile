FROM python:3-slim-bookworm

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

ENV FLAG=SSM{fake_flag}

CMD ["python3", "app.py"]